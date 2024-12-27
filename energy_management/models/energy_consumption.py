from odoo import models, fields, api
from odoo.exceptions import UserError
from datetime import timedelta
import numpy as np
from sklearn.linear_model import LinearRegression
import logging

_logger = logging.getLogger(__name__)

class EnergyConsumption(models.Model):
    _name = 'energy.consumption'
    _description = 'Monitoraggio del consumo energetico'

    name = fields.Char(string='Linea Produttiva', required=True)
    energy_usage = fields.Float(string='Consumo Energetico (kWh)', required=True)
    date = fields.Datetime(string='Data e Ora', default=fields.Datetime.now)
    suggestion = fields.Text(string='Suggerimento', compute='_generate_suggestion', store=True)
    total_consumption = fields.Float(string='Consumo Totale (kWh)', compute='_compute_total_consumption', store=True)
    prediction = fields.Float(string='Previsione Consumo (kWh)', compute='_compute_prediction', store=True)
    graph_color = fields.Char(string='Colore Grafico', compute='_compute_graph_color', store=False)
    type = fields.Selection([
        ('real', 'Consumo Reale'),
        ('predicted', 'Previsione')
    ], string='Tipo', required=True, default='real')
    machine_efficiency = fields.Float(string='Machine Efficiency')

    @api.depends('energy_usage')
    def _generate_suggestion(self, high_threshold=100, low_threshold=50):
        """Genera suggerimenti basati sui consumi."""
        for record in self:
            if record.energy_usage > high_threshold:
                record.suggestion = 'Ridurre il consumo durante le ore di punta.'
            elif record.energy_usage > low_threshold:
                record.suggestion = 'Monitorare i consumi.'
            else:
                record.suggestion = 'Consumo accettabile.'

    def check_high_consumption(self):
        """Controlla e notifica i consumi elevati."""
        high_consumption = self.search([('energy_usage', '>', 100)])
        if high_consumption:
            raise UserError(f"Attenzione! {len(high_consumption)} linee superano i consumi consentiti.")

    @api.depends('energy_usage')
    def _compute_total_consumption(self):
        for record in self:
            record.total_consumption = sum(self.env['energy.consumption'].search([]).mapped('energy_usage'))

    @api.depends('suggestion', 'energy_usage', 'prediction')
    def _compute_graph_color(self):
        """Assegna un colore al grafico in base al suggerimento."""
        for record in self:
            if record.suggestion == 'Ridurre il consumo durante le ore di punta.':
                record.graph_color = '#FF0000'  # Rosso
            elif record.suggestion == 'Monitorare i consumi.':
                record.graph_color = '#FFFF00'  # Giallo
            else:
                record.graph_color = '#00FF00'  # Verde

            # Differenzia i colori per le previsioni
            if record.type == 'predicted':
                record.graph_color = '#0000FF'  # Blu

    @api.model
    def create(self, vals):
        """Imposta il tipo corretto durante la creazione del record."""
        if 'prediction' in vals and vals['prediction'] > 0:
            vals['type'] = 'predicted'
        else:
            vals['type'] = 'real'
        return super(EnergyConsumption, self).create(vals)

    @api.depends('energy_usage', 'date')
    def _compute_prediction(self):
        for record in self:
            # Filtra solo i record della stessa linea produttiva
            consumptions = self.search([('name', '=', record.name)]).filtered(lambda r: r.date).sorted(
                key=lambda r: r.date)

            if len(consumptions) < 2:
                _logger.warning(f"Non ci sono abbastanza dati per calcolare una previsione per la linea {record.name}.")
                record.prediction = 0.0
                continue

            try:
                # Prepara i dati per il modello specifico della linea
                dates = np.array([(c.date - consumptions[0].date).total_seconds() for c in consumptions]).reshape(-1, 1)
                usages = np.array([c.energy_usage for c in consumptions])

                # Addestra il modello per la linea specifica
                model = LinearRegression()
                model.fit(dates, usages)

                # Prevedi il prossimo consumo (24 ore dopo l'ultimo record)
                next_date = (record.date - consumptions[0].date).total_seconds() + 24 * 3600
                record.prediction = model.predict([[next_date]])[0]

            except Exception as e:
                _logger.error(f"Errore nel calcolo della previsione per la linea {record.name}: {e}")
                record.prediction = 0.0



