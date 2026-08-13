import { CommonModule } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { MatButtonModule } from '@angular/material/button';
import { MatCardModule } from '@angular/material/card';

import { ClienteApiService } from '../../core/api/services/cliente.service';
import { ClienteRead } from '../../core/api/models/cliente.model';

@Component({
  selector: 'maia-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink, MatButtonModule, MatCardModule],
  templateUrl: './dashboard.component.html',
})
export class DashboardComponent implements OnInit {
  clientes = signal<ClienteRead[]>([]);

  constructor(private readonly clienteApi: ClienteApiService) {}

  ngOnInit(): void {
    this.clienteApi.listar().subscribe((clientes) => this.clientes.set(clientes));
  }
}
