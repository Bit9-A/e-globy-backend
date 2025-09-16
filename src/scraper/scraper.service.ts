import { Injectable, InternalServerErrorException } from '@nestjs/common';
import { spawn } from 'child_process';
import * as path from 'path';
import { InjectRepository } from '@nestjs/typeorm';
import { Repository } from 'typeorm';
import { Product } from '../database/entities/product.entity';
import { Store } from '../database/entities/store.entity';

@Injectable()
export class ScraperService {
  constructor(
    @InjectRepository(Product)
    private productRepository: Repository<Product>,
    @InjectRepository(Store)
    private storeRepository: Repository<Store>,
  ) {}

  async scrapeProducts(
    storeName: string,
    searchTerm: string,
    maxResults: number,
    page: number,
  ): Promise<Product[]> {
    return new Promise(async (resolve, reject) => {
      let pythonScriptPath: string;

      switch (storeName.toLowerCase()) {
        case 'amazon':
          pythonScriptPath = path.join(
            process.cwd(),
            '.',
            'src',
            'python',
            'scraper',
            'amazon',
            'amazon.search.products.py',
          );
          break;
        // Aquí se añadirán más casos para otras tiendas (ebay, walmart, etc.)
        default:
          return reject(
            new InternalServerErrorException(
              `Store ${storeName} not supported.`,
            ),
          );
      }

      // Obtener o crear la tienda
      let store = await this.storeRepository.findOne({
        where: { name: storeName },
      });
      if (!store) {
        store = this.storeRepository.create({ name: storeName });
        await this.storeRepository.save(store);
      }

      const pythonProcess = spawn('python', [
        pythonScriptPath,
        searchTerm,
        maxResults.toString(),
        page.toString(),
      ]);

      let data = '';
      let error = '';

      pythonProcess.stdout.on('data', (chunk) => {
        data += chunk.toString();
      });

      pythonProcess.stderr.on('data', (chunk) => {
        error += chunk.toString();
      });

      pythonProcess.on('close', async (code) => {
        if (code !== 0) {
          console.error(`Python script exited with code ${code}: ${error}`);
          return reject(
            new InternalServerErrorException(`Scraping failed: ${error}`),
          );
        }
        try {
          const scrapedProducts: any[] = JSON.parse(data);
          const savedProducts: Product[] = [];

          for (const scrapedProduct of scrapedProducts) {
            let product = await this.productRepository.findOne({
              where: {
                asin: scrapedProduct.ASIN,
                store: { store_id: store.store_id },
              },
            });

            if (product) {
              // Actualizar producto existente
              product.title = scrapedProduct.Title;
              product.price_current = parseFloat(scrapedProduct.Price);
              product.price_original = scrapedProduct['Price Original']
                ? parseFloat(scrapedProduct['Price Original'])
                : null;
              product.discount = scrapedProduct.Discount
                ? parseFloat(scrapedProduct.Discount.replace('%', ''))
                : null;
              product.image_url = scrapedProduct['Image URL'];
              product.product_url = scrapedProduct['Product URL'];
              product.last_scraped_date = new Date();
            } else {
              // Crear nuevo producto
              product = this.productRepository.create({
                asin: scrapedProduct.ASIN,
                title: scrapedProduct.Title,
                price_current: parseFloat(scrapedProduct.Price),
                price_original: scrapedProduct['Price Original']
                  ? parseFloat(scrapedProduct['Price Original'])
                  : null,
                discount: scrapedProduct.Discount
                  ? parseFloat(scrapedProduct.Discount.replace('%', ''))
                  : null,
                image_url: scrapedProduct['Image URL'],
                product_url: scrapedProduct['Product URL'],
                last_scraped_date: new Date(),
                store_id: store.store_id, // Asignar store_id directamente
                store: store,
              });
            }
            savedProducts.push(await this.productRepository.save(product));
          }
          resolve(savedProducts);
        } catch (e) {
          console.error(
            'Failed to parse JSON from Python script or save to DB:',
            e,
          );
          console.error('Python script raw output:', data);
          console.error('Python script error output:', error);
          reject(
            new InternalServerErrorException(
              'Failed to process scraping results or save to database.',
            ),
          );
        }
      });

      pythonProcess.on('error', (err) => {
        console.error('Failed to start Python subprocess:', err);
        reject(
          new InternalServerErrorException('Failed to start scraping process.'),
        );
      });
    });
  }
}
