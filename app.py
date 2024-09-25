from flask import Flask, request, render_template
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv
import os
app = Flask(__name__)
 
# Load environment variables from .env file
load_dotenv()

# Replace these with your Azure Storage account credentials
account_name = 'agbyos'

account_key = os.getenv('AZURE_BLOB_SECRET_KEY')
# account_key = 
container_name = 'agblob'
 
# Create a BlobServiceClient
blob_service_client = BlobServiceClient(account_url=f"https://{account_name}.blob.core.windows.net", credential=account_key)
container_client = blob_service_client.get_container_client(container_name)
 
@app.route('/')
def index():
    return render_template('index.html')
 
@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        return 'No file part'
    
    file = request.files['file']
    
    if file.filename == '':
        return 'No selected file'
    
    # Upload file to Azure Blob Storage
    blob_client = container_client.get_blob_client(file.filename)
    blob_client.upload_blob(file)
    
    return 'File uploaded successfully'


# Function to get all file names from Azure Blob Storage
def get_blob_names():
    blob_names = []
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        blob_names.append(blob.name)
    return blob_names

# Route to display file names
@app.route('/list')
def list():
    blob_names = get_blob_names()
    return render_template('list.html', blob_names=blob_names)



from flask import Flask, render_template, request, redirect, url_for


# Function to delete a file from Azure Blob Storage
def delete_blob(blob_name):
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.delete_blob()



# Route to delete files
@app.route('/delete', methods=['GET', 'POST'])
def delete():
    if request.method == 'POST':
        file_name = request.form['file_name']
        delete_blob(file_name)
        return redirect(url_for('list'))
    return render_template('delete.html')

# Route to delete all files
@app.route('/delete-all', methods=['POST'])
def delete_all():
    blob_list = container_client.list_blobs()
    for blob in blob_list:
        delete_blob(blob.name)
    return redirect(url_for('index'))
 
if __name__ == '__main__':
    app.run(debug=True)