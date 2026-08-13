import { Injectable, signal } from '@angular/core';

export interface Breadcrumb {
  label: string;
  link?: string[];
}

@Injectable({ providedIn: 'root' })
export class PageHeaderService {
  readonly breadcrumbs = signal<Breadcrumb[]>([]);

  set(breadcrumbs: Breadcrumb[]): void {
    this.breadcrumbs.set(breadcrumbs);
  }
}
