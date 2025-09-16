import { Injectable, InternalServerErrorException } from '@nestjs/common';
import { spawn } from 'child_process';
import * as path from 'path';

@Injectable()
export class ScraperService {
  async scrapeProducts(searchTerm: string, maxResults: number): Promise<any[]> {
    return new Promise((resolve, reject) => {
      const pythonScriptPath = path.join(
        process.cwd(),
        '..', // Subir un nivel para llegar a E-Globy
        'prueba-api-ebay',
        'app.py',
      );
      const pythonProcess = spawn('python', [
        pythonScriptPath,
        searchTerm,
        maxResults.toString(),
      ]);

      let data = '';
      let error = '';

      pythonProcess.stdout.on('data', (chunk) => {
        data += chunk.toString();
      });

      pythonProcess.stderr.on('data', (chunk) => {
        error += chunk.toString();
      });

      pythonProcess.on('close', (code) => {
        if (code !== 0) {
          console.error(`Python script exited with code ${code}: ${error}`);
          return reject(
            new InternalServerErrorException(`Scraping failed: ${error}`),
          );
        }
        try {
          const result = JSON.parse(data);
          resolve(result);
        } catch (e) {
          console.error('Failed to parse JSON from Python script:', e);
          console.error('Python script raw output:', data);
          console.error('Python script error output:', error);
          reject(
            new InternalServerErrorException(
              'Failed to parse scraping results.',
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
