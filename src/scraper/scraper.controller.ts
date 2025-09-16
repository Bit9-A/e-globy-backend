import {
  Controller,
  Get,
  Query,
  InternalServerErrorException,
} from '@nestjs/common';
import { ScraperService } from './scraper.service';

@Controller('scraper')
export class ScraperController {
  constructor(private readonly scraperService: ScraperService) {}

  @Get('products')
  async getScrapedProducts(
    @Query('searchTerm') searchTerm: string,
    @Query('maxResults') maxResults: string,
  ): Promise<any[]> {
    if (!searchTerm) {
      throw new InternalServerErrorException('Search term is required.');
    }
    const numMaxResults = maxResults ? parseInt(maxResults, 10) : 5;
    if (isNaN(numMaxResults) || numMaxResults < 1 || numMaxResults > 20) {
      throw new InternalServerErrorException(
        'maxResults must be a number between 1 and 20.',
      );
    }

    try {
      return await this.scraperService.scrapeProducts(
        searchTerm,
        numMaxResults,
      );
    } catch (error) {
      throw new InternalServerErrorException(error.message);
    }
  }
}
