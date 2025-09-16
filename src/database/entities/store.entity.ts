import { Entity, PrimaryGeneratedColumn, Column, OneToMany } from 'typeorm';
import { Product } from './product.entity';

@Entity('stores')
export class Store {
  @PrimaryGeneratedColumn()
  store_id: number;

  @Column({ unique: true, nullable: false })
  name: string;

  @OneToMany(() => Product, (product) => product.store)
  products: Product[];
}
