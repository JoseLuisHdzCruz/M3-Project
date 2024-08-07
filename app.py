from flask import Flask, request, jsonify
import pandas as pd
import joblib
from flask_cors import CORS  # Importa CORS
# import requests
from sklearn.preprocessing import StandardScaler, OrdinalEncoder
from scipy.cluster.hierarchy import fcluster

app = Flask(__name__)

# Configurar CORS
CORS(app)  # Habilita CORS para todas las rutas

# Cargar los modelos y el preprocesador
encoder = joblib.load('encoder.pkl')
scaler = joblib.load('scaler.pkl')
linkage_model = joblib.load('linkage_model.pkl')
n_clusters = joblib.load('n_clusters.pkl')

# Ruta del archivo CSV
csv_file = 'Ventas.csv'

@app.route('/predict', methods=['GET'])
def predict():
    # Cargar datos desde el archivo CSV
    df = pd.read_csv(csv_file)

    # Preprocesar los datos
    df['total'] = encoder.transform(df[['total']])
    df[['cantidad', 'total']] = scaler.transform(df[['cantidad', 'total']])

    # Realizar la predicción de clusters
    y_hc = fcluster(linkage_model, t=n_clusters, criterion='maxclust')
    df['cluster'] = y_hc

    # Identificar el cluster con los valores más altos de 'total' y 'cantidad'
    cluster_summary = df.groupby('cluster')[['cantidad', 'total']].mean()
    cluster_summary['suma'] = cluster_summary['cantidad'] + cluster_summary['total']
    max_cluster = cluster_summary['suma'].idxmax()

    # Obtener customerId del cluster con mayor 'total' y 'cantidad'
    max_customers = df[df['cluster'] == max_cluster]['customerId'].unique()

    response = {
        'max_customers': max_customers.tolist(),
        'num_max_customers': len(max_customers)
    }

    return jsonify(response)

if __name__ == '__main__':
    app.run(debug=True)