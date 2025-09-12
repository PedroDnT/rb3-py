"""Readers for B3 data files.

This module provides specialized readers for different types of B3 data files.
"""

import re
import datetime
from io import StringIO

import pandas as pd
from bs4 import BeautifulSoup

def read_cotahist_file(file_path):
    """Read COTAHIST file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        pandas.DataFrame: Data frame with COTAHIST data
    """
    # Define column specifications for fixed-width file
    colspecs = [
        (0, 2),      # TIPREG - Tipo de registro
        (2, 10),     # DATA - Data do pregão
        (10, 12),    # CODBDI - Código BDI
        (12, 24),    # CODNEG - Código de negociação
        (24, 27),    # TPMERC - Tipo de mercado
        (27, 39),    # NOMRES - Nome resumido
        (39, 49),    # ESPECI - Especificação
        (49, 52),    # PRAZOT - Prazo em dias
        (52, 56),    # MODREF - Moeda de referência
        (56, 69),    # PREABE - Preço de abertura
        (69, 82),    # PREMAX - Preço máximo
        (82, 95),    # PREMIN - Preço mínimo
        (95, 108),   # PREMED - Preço médio
        (108, 121),  # PREULT - Preço do último negócio
        (121, 134),  # PREOFC - Preço da melhor oferta de compra
        (134, 147),  # PREOFV - Preço da melhor oferta de venda
        (147, 152),  # TOTNEG - Número de negócios
        (152, 170),  # QUATOT - Quantidade total de títulos
        (170, 188),  # VOLTOT - Volume total
        (188, 201),  # PREEXE - Preço de exercício
        (201, 202),  # INDOPC - Indicador de correção de preços
        (202, 210),  # DATVEN - Data de vencimento
        (210, 217),  # FATCOT - Fator de cotação
        (217, 230),  # PTOEXE - Ponto de exercício
        (230, 242),  # CODISI - Código ISIN
        (242, 245),  # DISMES - Número de distribuição
    ]
    
    # Define column names
    names = [
        'tipreg', 'refdate', 'codbdi', 'symbol', 'tpmerc', 'name',
        'especi', 'prazot', 'modref', 'open', 'high', 'low', 'average',
        'close', 'bid', 'ask', 'trades', 'quantity', 'volume',
        'strike', 'indopc', 'maturity', 'fatcot', 'ptoexe', 'isin', 'dismes'
    ]
    
    # Read the file
    df = pd.read_fwf(
        file_path,
        colspecs=colspecs,
        names=names,
        skiprows=1,  # Skip header
        skipfooter=1  # Skip footer
    )
    
    # Convert date columns
    df['refdate'] = pd.to_datetime(df['refdate'], format='%Y%m%d')
    df['maturity'] = pd.to_datetime(df['maturity'], format='%Y%m%d', errors='coerce')
    
    # Convert numeric columns
    for col in ['open', 'high', 'low', 'average', 'close', 'bid', 'ask', 'strike', 'volume']:
        df[col] = df[col] / 100.0  # Prices are multiplied by 100 in the file
    
    # Determine instrument type
    def determine_type(row):
        if row['tpmerc'] == 10:  # Vista
            if row['especi'] in ['ON', 'PN', 'PNA', 'PNB', 'PNC', 'PND']:
                return 'EQUITY'
            elif row['especi'] == 'UNT':
                return 'UNIT'
            elif row['especi'] == 'ETF':
                return 'ETF'
            elif row['especi'] == 'BDR':
                return 'BDR'
            elif row['especi'] == 'FII':
                return 'REIT'
        elif row['tpmerc'] in [70, 80]:  # Opções
            return 'OPTION'
        elif row['tpmerc'] == 2:  # Futuro
            return 'FUTURE'
        return 'OTHER'
    
    df['type'] = df.apply(determine_type, axis=1)
    
    return df

def read_futures_settlement_prices(file_path):
    """Read futures settlement prices file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        pandas.DataFrame: Data frame with futures settlement prices
    """
    # Read the HTML file
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the date
    date_text = soup.find('h3', class_='center').text.strip()
    date_match = re.search(r'\d{2}/\d{2}/\d{4}', date_text)
    if date_match:
        refdate = datetime.datetime.strptime(date_match.group(), '%d/%m/%Y').date()
    else:
        refdate = None
    
    # Find the tables
    tables = soup.find_all('table', class_='tabela')
    
    # Process each table
    data = []
    for table in tables:
        # Get the ticker from the table header
        header = table.find('th').text.strip()
        ticker_match = re.search(r'\b([A-Z]{3})\b', header)
        if ticker_match:
            ticker = ticker_match.group(1)
        else:
            continue
        
        # Process the rows
        rows = table.find_all('tr')[1:]  # Skip header row
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                maturity = cols[0].text.strip()
                settlement_price = cols[1].text.strip().replace('.', '').replace(',', '.')
                variation = cols[2].text.strip().replace('.', '').replace(',', '.')
                
                # Skip empty rows
                if not maturity or not settlement_price:
                    continue
                
                # Convert maturity to date
                maturity_match = re.search(r'([A-Z])/(\d{2})', maturity)
                if maturity_match:
                    month_code = maturity_match.group(1)
                    year = '20' + maturity_match.group(2)
                    maturity_date = f"{month_code}{year}"
                else:
                    maturity_date = None
                
                data.append({
                    'refdate': refdate,
                    'ticker': ticker,
                    'maturity': maturity,
                    'maturity_code': maturity_date,
                    'settlement_price': float(settlement_price) if settlement_price else None,
                    'variation': float(variation) if variation else None
                })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    return df

def read_reference_rates(file_path):
    """Read reference rates (yield curves) file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        pandas.DataFrame: Data frame with reference rates
    """
    # Read the HTML file
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the date
    date_text = soup.find('h3', class_='center').text.strip()
    date_match = re.search(r'\d{2}/\d{2}/\d{4}', date_text)
    if date_match:
        refdate = datetime.datetime.strptime(date_match.group(), '%d/%m/%Y').date()
    else:
        refdate = None
    
    # Find the curve name
    title = soup.find('h2', class_='center').text.strip()
    if 'PRÉ' in title:
        curve_name = 'PRE'
    elif 'DI x IPCA' in title:
        curve_name = 'DIC'
    elif 'DI x IGP-M' in title:
        curve_name = 'DOC'
    else:
        curve_name = None
    
    # Find the table
    table = soup.find('table', class_='tabela')
    if not table:
        return pd.DataFrame()
    
    # Process the rows
    data = []
    rows = table.find_all('tr')[1:]  # Skip header row
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 3:
            days = cols[0].text.strip()
            date = cols[1].text.strip()
            rate = cols[2].text.strip().replace('.', '').replace(',', '.')
            
            # Skip empty rows
            if not days or not date or not rate:
                continue
            
            # Convert date
            try:
                forward_date = datetime.datetime.strptime(date, '%d/%m/%Y').date()
            except:
                forward_date = None
            
            data.append({
                'refdate': refdate,
                'curve_name': curve_name,
                'days': int(days) if days.isdigit() else None,
                'forward_date': forward_date,
                'r_252': float(rate) / 100.0 if rate else None  # Convert percentage to decimal
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    return df

def read_indexes_composition(file_path):
    """Read indexes composition file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        pandas.DataFrame: Data frame with indexes composition
    """
    # Read the HTML file
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find all index links
    index_links = soup.find_all('a', href=re.compile(r'indices-amplos/indice-.*-composicao-da-carteira.htm'))
    
    # Extract index codes
    indexes = []
    for link in index_links:
        href = link['href']
        match = re.search(r'indice-(\w+)-', href)
        if match:
            index_code = match.group(1).upper()
            indexes.append(index_code)
    
    # Create DataFrame
    df = pd.DataFrame({'index': indexes})
    
    return df

def read_indexes_portfolio(file_path):
    """Read index portfolio file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        pandas.DataFrame: Data frame with index portfolio
    """
    # Read the HTML file
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # Parse the HTML
    soup = BeautifulSoup(html, 'html.parser')
    
    # Find the index name
    title = soup.find('h2', class_='title').text.strip()
    match = re.search(r'Índice\s+(\w+)', title)
    if match:
        index = match.group(1).upper()
    else:
        index = None
    
    # Find the table
    table = soup.find('table', class_='tabela')
    if not table:
        return pd.DataFrame()
    
    # Process the rows
    data = []
    rows = table.find_all('tr')[1:]  # Skip header row
    for row in rows:
        cols = row.find_all('td')
        if len(cols) >= 4:
            code = cols[0].text.strip()
            company = cols[1].text.strip()
            type_str = cols[2].text.strip()
            weight = cols[3].text.strip().replace('.', '').replace(',', '.')
            
            # Skip empty rows
            if not code or not company:
                continue
            
            data.append({
                'index': index,
                'code': code,
                'company': company,
                'type': type_str,
                'weight': float(weight) / 100.0 if weight else None  # Convert percentage to decimal
            })
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    return df

def read_indexes_historical_data(file_path):
    """Read historical index data file.
    
    Args:
        file_path (str): Path to the file
        
    Returns:
        pandas.DataFrame: Data frame with historical index data
    """
    # Determine file type based on extension
    if file_path.endswith('.xlsx') or file_path.endswith('.xls'):
        df = pd.read_excel(file_path)
    elif file_path.endswith('.csv'):
        df = pd.read_csv(file_path, sep=';', decimal=',')
    else:
        return pd.DataFrame()
    
    # Standardize column names
    df.columns = [col.lower().strip() for col in df.columns]
    
    # Rename columns
    column_mapping = {
        'data': 'date',
        'abertura': 'open',
        'mínimo': 'low',
        'máximo': 'high',
        'fechamento': 'close',
        'volume': 'volume'
    }
    
    df = df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns})
    
    # Convert date column
    if 'date' in df.columns:
        df['date'] = pd.to_datetime(df['date'], errors='coerce')
    
    # Convert numeric columns
    for col in ['open', 'low', 'high', 'close']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df