import { Module } from '@nestjs/common';
import { TypeOrmModule } from '@nestjs/typeorm';
import { ScraperService } from './scraper.service';
import { ScraperController } from './scraper.controller';
import { Product } from '../database/entities/product.entity';
import { Store } from '../database/entities/store.entity';

@Module({
  imports: [TypeOrmModule.forFeature([Product, Store])],
  providers: [ScraperService],
  controllers: [ScraperController],
})
export class ScraperModule {}
