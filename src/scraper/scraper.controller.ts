import {
  Controller,
  Get,
  Query,
  InternalServerErrorException,
} from '@nestjs/common';
import { ScraperService } from './scraper.service';

@Controller('product')
export class ScraperController {
  constructor(private readonly scraperService: ScraperService) {}

  @Get('search')
  async getScrapedProducts(
    @Query('store') store: string,
    @Query('searchTerm') searchTerm: string,
    @Query('maxResults') maxResults: string,
    @Query('page') page: string,
  ): Promise<any[]> {
    if (!store) {
      throw new InternalServerErrorException('Store is required.');
    }
    if (!searchTerm) {
      throw new InternalServerErrorException('Search term is required.');
    }

    const numMaxResults = maxResults ? parseInt(maxResults, 10) : 5;
    if (isNaN(numMaxResults) || numMaxResults < 1 || numMaxResults > 100) {
      throw new InternalServerErrorException(
        'maxResults must be a number between 1 and 100.',
      );
    }

    const pageNumber = page ? parseInt(page, 10) : 1;
    if (isNaN(pageNumber) || pageNumber < 1) {
      throw new InternalServerErrorException('Page must be a positive number.');
    }

    try {
      return await this.scraperService.scrapeProducts(
        store,
        searchTerm,
        numMaxResults,
        pageNumber,
      );
    } catch (error) {
      throw new InternalServerErrorException(error.message);
    }
  }
}
