import os
import pdfplumber
import re
from datetime import datetime
from pathlib import Path


class NotaFiscalParser:
    def __init__(self, pdf_path):
        self.pdf_path = pdf_path
        self.dados_extraidos = {
            'nome_empresa': None,
            'data_emissao': None,
            'data_vencimento': None,
            'valor_total': None,
            'quantidade_parcelas': None,
            'itens': []
        }

    def extrair_dados(self):
        with pdfplumber.open(self.pdf_path) as pdf:
            texto_completo = ""

            # Extrair texto de todas as páginas
            for pagina in pdf.pages:
                texto_completo += pagina.extract_text() + "\n"

            # Extrair nome da empresa
            padrao_empresa = r"RAZÃO SOCIAL:[\s\n]*([^\n]+)"
            match_empresa = re.search(padrao_empresa, texto_completo, re.IGNORECASE)
            if match_empresa:
                self.dados_extraidos['nome_empresa'] = match_empresa.group(1).strip()

            # Extrair data de emissão
            padrao_emissao = r"DATA\s+D[AE]\s+EMISSÃO:[\s\n]*(\d{2}/\d{2}/\d{4})"
            match_emissao = re.search(padrao_emissao, texto_completo, re.IGNORECASE)
            if match_emissao:
                self.dados_extraidos['data_emissao'] = self._formatar_data(match_emissao.group(1))

            # Extrair data de vencimento
            padrao_vencimento = r"DATA\s+D[OE]\s+VENCIMENTO:[\s\n]*(\d{2}/\d{2}/\d{4})"
            match_vencimento = re.search(padrao_vencimento, texto_completo, re.IGNORECASE)
            if match_vencimento:
                self.dados_extraidos['data_vencimento'] = self._formatar_data(match_vencimento.group(1))

            # Extrair valor total
            padrao_valor = r"VALOR\s+TOTAL:[\s\n]*R?\$?\s*([\d.,]+)"
            match_valor = re.search(padrao_valor, texto_completo, re.IGNORECASE)
            if match_valor:
                valor_texto = match_valor.group(1).replace(".", "").replace(",", ".")
                self.dados_extraidos['valor_total'] = float(valor_texto)

            # Extrair quantidade de parcelas
            padrao_parcelas = r"PARCELAS?:[\s\n]*(\d+)"
            match_parcelas = re.search(padrao_parcelas, texto_completo, re.IGNORECASE)
            if match_parcelas:
                self.dados_extraidos['quantidade_parcelas'] = int(match_parcelas.group(1))
            else:
                # Se não encontrar parcelas explicitamente, assume 1
                self.dados_extraidos['quantidade_parcelas'] = 1

            # Extrair itens da nota
            # Esta é uma abordagem simplificada; pode precisar de ajustes para seu formato específico
            padrao_itens = r"ITEM\s+DESCRIÇÃO.*?\n(.*?)(?:VALOR TOTAL|TOTAL GERAL)"
            match_itens = re.search(padrao_itens, texto_completo, re.IGNORECASE | re.DOTALL)

            if match_itens:
                texto_itens = match_itens.group(1)
                linhas_itens = texto_itens.strip().split('\n')

                for linha in linhas_itens:
                    if re.search(r'\d', linha):  # Verifica se a linha contém algum número
                        # Remove espaços extras e formata a descrição do item
                        item_formatado = re.sub(r'\s+', ' ', linha).strip()
                        if item_formatado:
                            self.dados_extraidos['itens'].append(item_formatado)

        return self.dados_extraidos

    def _formatar_data(self, data_texto):
        """Converte string de data para formato YYYY-MM-DD"""
        try:
            data = datetime.strptime(data_texto, "%d/%m/%Y")
            return data.strftime("%Y-%m-%d")
        except ValueError:
            return None


def processar_nota_fiscal(caminho_pdf):
    """Função auxiliar para processar um arquivo PDF de nota fiscal"""
    parser = NotaFiscalParser(caminho_pdf)
    return parser.extrair_dados()
