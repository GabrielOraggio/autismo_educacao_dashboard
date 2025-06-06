import pandas as pd

def clean_education_data(df):
    """Limpeza dos dados de educação"""
    df = df.dropna(subset=['matriculas_autismo', 'total_matriculas'])
    df['percentual_autismo'] = (df['matriculas_autismo'] / df['total_matriculas']) * 100
    return df

def calculate_growth_rates(df):
    """Calcula taxas de crescimento anual"""
    df = df.sort_values(['regiao', 'tipo_escola', 'ano'])
    df['crescimento_anual'] = df.groupby(['regiao', 'tipo_escola'])['matriculas_autismo'].pct_change() * 100
    return df