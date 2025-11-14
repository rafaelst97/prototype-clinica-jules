import requests
import json

# Fazer login
print("Fazendo login...")
login_response = requests.post('http://localhost:8000/auth/login', json={
    'email': 'paciente1@teste.com',
    'senha': 'paciente123'
})

print(f"Status do login: {login_response.status_code}")
print(f"Response do login: {login_response.text}")

if login_response.status_code == 200:
    login_data = login_response.json()
    token = login_data.get('access_token')
    
    if token:
        print(f"\nToken obtido: {token[:50]}...")
        
        # Testar endpoint de consultas
        print("\nTestando endpoint de consultas...")
        headers = {'Authorization': f'Bearer {token}'}
        consultas_response = requests.get('http://localhost:8000/pacientes/consultas', headers=headers)
        
        print(f"Status: {consultas_response.status_code}")
        print(f"Response: {consultas_response.text}")
    else:
        print("Token não encontrado na resposta")
        print(f"Keys disponíveis: {login_data.keys()}")
