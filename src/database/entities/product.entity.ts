import {
  Entity,
  PrimaryGeneratedColumn,
  Column,
  ManyToOne,
  Index,
} from 'typeorm';
import { Store } from './store.entity';

@Entity('products')
@Index(['asin', 'store_id'], { unique: true }) // Asegura que ASIN sea único por tienda
export class Product {
  @PrimaryGeneratedColumn()
  product_id: number;

  @Column({ length: 50, unique: false, nullable: false }) // ASIN ya no es globalmente único, sino por tienda
  asin: string;

  @Column({ length: 255, nullable: false })
  title: string;

  @Column({ type: 'numeric', precision: 10, scale: 2, nullable: false })
  price_current: number;

  @Column({ type: 'numeric', precision: 10, scale: 2, nullable: true })
  price_original: number | null; // Permitir null

  @Column({ type: 'numeric', precision: 5, scale: 2, nullable: true })
  discount: number | null; // Permitir null

  @Column({ length: 255, nullable: true })
  image_url: string;

  @Column({ type: 'text', nullable: false }) // Cambiado a TEXT para URLs largas
  product_url: string;

  @Column({ type: 'timestamptz', default: () => 'NOW()' })
  last_scraped_date: Date;

  @Column({ nullable: false })
  store_id: number;

  @ManyToOne(() => Store, (store) => store.products)
  store: Store;
}
