"""Downloaders for B3 data.

This module provides specialized downloaders for different types of B3 data.
"""

import os
import re
import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

def download_cotahist_yearly(output_path, year):
    """Download yearly COTAHIST file.
    
    Args:
        output_path (str): Path to save the file
        year (int): Year to download
        
    Returns:
        bool: Whether the download was successful
    """
    url = f"https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_A{year}.ZIP"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"Error downloading COTAHIST for year {year}: {e}")
        return False

def download_cotahist_daily(output_path, date):
    """Download daily COTAHIST file.
    
    Args:
        output_path (str): Path to save the file
        date (datetime.date): Date to download
        
    Returns:
        bool: Whether the download was successful
    """
    date_str = date.strftime("%d%m%Y")
    url = f"https://bvmf.bmfbovespa.com.br/InstDados/SerHist/COTAHIST_D{date_str}.ZIP"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"Error downloading COTAHIST for date {date_str}: {e}")
        return False

def download_futures_settlement_prices(output_path, refdate):
    """Download futures settlement prices.
    
    Args:
        output_path (str): Path to save the file
        refdate (datetime.date): Reference date
        
    Returns:
        bool: Whether the download was successful
    """
    date_str = refdate.strftime("%Y-%m-%d")
    url = f"https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-ajustes-do-pregao-ptBR.asp?Data={date_str}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return True
    except Exception as e:
        print(f"Error downloading futures settlement prices for date {date_str}: {e}")
        return False

def download_reference_rates(output_path, refdate, curve_name):
    """Download reference rates (yield curves).
    
    Args:
        output_path (str): Path to save the file
        refdate (datetime.date): Reference date
        curve_name (str): Curve name (e.g., 'PRE', 'DIC', 'DOC')
        
    Returns:
        bool: Whether the download was successful
    """
    date_str = refdate.strftime("%Y-%m-%d")
    
    # Map curve names to B3 codes
    curve_codes = {
        'PRE': 'PRE',
        'DIC': 'DIC',
        'DOC': 'DOC',
    }
    
    curve_code = curve_codes.get(curve_name)
    if not curve_code:
        print(f"Unknown curve name: {curve_name}")
        return False
    
    url = f"https://www2.bmf.com.br/pages/portal/bmfbovespa/lumis/lum-taxas-referenciais-ptBR.asp?Data={date_str}&Data1=&slcTaxa={curve_code}"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return True
    except Exception as e:
        print(f"Error downloading reference rates for date {date_str} and curve {curve_name}: {e}")
        return False

def download_indexes_composition(output_path):
    """Download indexes composition.
    
    Args:
        output_path (str): Path to save the file
        
    Returns:
        bool: Whether the download was successful
    """
    url = "https://www.b3.com.br/pt_br/produtos-e-servicos/indices/indices-amplos/indice-ibovespa-ibovespa-composicao-da-carteira.htm"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return True
    except Exception as e:
        print(f"Error downloading indexes composition: {e}")
        return False

def download_indexes_portfolio(output_path, index):
    """Download index portfolio.
    
    Args:
        output_path (str): Path to save the file
        index (str): Index name (e.g., 'IBOV', 'IBXX', 'SMLL')
        
    Returns:
        bool: Whether the download was successful
    """
    # Map index names to B3 codes
    index_codes = {
        'IBOV': 'IBOV',
        'IBXX': 'IBXX',
        'SMLL': 'SMLL',
        'MLCX': 'MLCX',
        'IDIV': 'IDIV',
        'ICON': 'ICON',
        'IMOB': 'IMOB',
        'IFNC': 'IFNC',
        'IMAT': 'IMAT',
        'UTIL': 'UTIL',
        'INDX': 'INDX',
    }
    
    index_code = index_codes.get(index)
    if not index_code:
        print(f"Unknown index: {index}")
        return False
    
    url = f"https://www.b3.com.br/pt_br/produtos-e-servicos/indices/indices-amplos/indice-{index_code.lower()}-composicao-da-carteira.htm"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(response.text)
        
        return True
    except Exception as e:
        print(f"Error downloading index portfolio for {index}: {e}")
        return False

def download_indexes_historical_data(output_path, index, year):
    """Download historical index data.
    
    Args:
        output_path (str): Path to save the file
        index (str): Index name (e.g., 'IBOV', 'IBXX', 'SMLL')
        year (int): Year to download
        
    Returns:
        bool: Whether the download was successful
    """
    # Map index names to B3 codes
    index_codes = {
        'IBOV': 'IBOVESPA',
        'IBXX': 'IBX',
        'SMLL': 'SMLL',
        'MLCX': 'MLCX',
        'IDIV': 'IDIV',
        'ICON': 'ICON',
        'IMOB': 'IMOB',
        'IFNC': 'IFNC',
        'IMAT': 'IMAT',
        'UTIL': 'UTIL',
        'INDX': 'INDX',
    }
    
    index_code = index_codes.get(index)
    if not index_code:
        print(f"Unknown index: {index}")
        return False
    
    url = f"https://www.b3.com.br/pt_br/market-data-e-indices/indices/indices-amplos/indice-{index_code.lower()}-{index.lower()}-estatisticas-historicas.htm"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        
        # Find the download link for the specified year
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a', href=True)
        
        download_url = None
        for link in links:
            if str(year) in link.text and index_code in link.text:
                download_url = link['href']
                break
        
        if not download_url:
            print(f"No download link found for index {index} and year {year}")
            return False
        
        # Download the file
        response = requests.get(download_url)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            f.write(response.content)
        
        return True
    except Exception as e:
        print(f"Error downloading historical data for index {index} and year {year}: {e}")
        return False