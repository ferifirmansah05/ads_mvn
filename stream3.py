import streamlit as st
from datetime import datetime
import pandas as pd
import json
import os
import base64
import zipfile
import tempfile
import re
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import google_auth_oauthlib.flow
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError

st.title('Download Invoice')

# Jika memodifikasi scope, hapus file token.json
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly', 'https://www.googleapis.com/auth/gmail.modify']

redirect_uri = os.environ.get("REDIRECT_URI", 'urn:ietf:wg:oauth:2.0:oob')

from streamlit_js import st_js, st_js_blocking

def ls_get(k, key=None):
    return st_js_blocking(f"return JSON.parse(localStorage.getItem('{k}'));", key)

def ls_set(k, v, key=None):
    jdata = json.dumps(v, ensure_ascii=False)
    st_js_blocking(f"localStorage.setItem('{k}', JSON.stringify({jdata}));", key)

def init_session():
    user_info = ls_get("user_info")
    if user_info:
        st.session_state["user_info"] = user_info

def auth_flow():
    auth_code = st.query_params.get("code")
    flow = google_auth_oauthlib.flow.Flow.from_client_secrets_file(
        'credentials_shopee.json',  # replace with your json credentials from your google auth app
        scopes=SCOPES,
        redirect_uri=redirect_uri,
    )
    if auth_code:
        flow.fetch_token(code=auth_code)
        credentials = flow.credentials
        st.write("Login Done")
        user_info_service = build(
            serviceName="oauth2",
            version="v2",
            credentials=credentials,
        )
        user_info = user_info_service.userinfo().get().execute()
        assert user_info.get("email"), "Email not found in infos"
        st.session_state["google_auth_code"] = auth_code
        st.session_state["user_info"] = user_info
        ls_set("user_info", user_info)
    else:
        authorization_url, state = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
        )
        st.link_button("Sign in with Google", authorization_url)


def authenticate_gmail(authorization_code):
    """Authenticate and return Gmail API service."""
    creds = None
    # Token file untuk menyimpan kredensial yang telah diakses sebelumnya.
    try:
        creds = InstalledAppFlow.from_client_secrets_file('credentials_shopee.json', SCOPES, redirect_uri='urn:ietf:wg:oauth:2.0:oob').fetch_token(code=authorization_code) 
    except InvalidGrantError as error:
        creds = ''
        st.write(f'Kode Otorisasi Tidak Valid: {error}')
        
    dt = datetime.utcfromtimestamp(creds['expires_at'])

    # Formatkan datetime ke dalam format ISO 8601
    formatted_time = dt.isoformat() + "Z"
    token_info = {
                'token': creds['access_token'],
                'refresh_token': creds['refresh_token'],
                'token_uri': 'https://oauth2.googleapis.com/token',
                'client_id': '142587760391-6krquvi7s3buhm3tnla7obahcq99305j.apps.googleusercontent.com',
                'client_secret': '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',
                'scopes': creds['scope'],
                'expiry': formatted_time
            }
    with open('token.json', 'w') as token_file:
        json.dump(token_info, token_file)

    return build('gmail', 'v1', credentials=Credentials.from_authorized_user_file('token.json', SCOPES))
    
def list_messages(service, query):
    """List email messages based on a query."""
    try:
        results = service.users().messages().list(userId='me', q=query).execute()
        messages = results.get('messages', [])
        return messages
    except HttpError as error:
        st.write(f'An error occurred: {error}')
        return []
    
def get_message(service, msg_id):
    """Get a specific email message."""
    try:
        msg = service.users().messages().get(userId='me', id=msg_id).execute()
        return msg
    except HttpError as error:
        st.write(f'An error occurred: {error}')
        return None

def save_attachment(service, msg_id, store_dir='downloads'):
    """Download attachment if it's a CSV file."""
    msg = get_message(service, msg_id)
    if not msg:
        return
    
    for part in msg['payload']['parts']:
        if 'filename' in part and part['filename']:
            file_name = part['filename']
            if file_name.endswith('.csv'):
                attachment = service.users().messages().attachments().get(
                    userId='me', messageId=msg_id, id=part['body']['attachmentId']).execute()
                data = base64.urlsafe_b64decode(attachment['data'].encode('UTF-8'))

                if not os.path.exists(store_dir):
                    os.makedirs(store_dir)

                file_path = os.path.join(store_dir, file_name)
                with open(file_path, 'wb') as f:
                    f.write(data)
                st.write(f'Attachment {file_name} saved to {file_path}')
                
def create_zip_from_folder(folder_path, zip_filename):
    # Membuat file zip dan menambahkan file CSV dari folder
    with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for folder_name, subfolders, filenames in os.walk(folder_path):
            for filename in filenames:
                if filename.endswith('.csv'):  # Menambahkan hanya file CSV
                    file_path = os.path.join(folder_name, filename)
                    # Menambahkan file ke dalam zip dengan path relatif dari folder_path
                    arcname = os.path.relpath(file_path, folder_path)
                    zipf.write(file_path, arcname)

uploaded_file = st.file_uploader("Pilih file Excel", type="xlsx")


if "button1" not in st.session_state:
    st.session_state["button1"] = False
if "button2" not in st.session_state:
    st.session_state["button2"] = False

if uploaded_file:
    db = pd.read_excel(uploaded_file)
    jumlah = st.slider('Pilih total file terakhir yang akan didownload', min_value=1, max_value=7, value=3)
    all_cab = st.multiselect('Pilih Cabang', db['CAB'].to_list(), default=db['CAB'].to_list())
    db = db[db['CAB'].isin(all_cab)].reset_index(drop=True)
    gojek, shopee = st.tabs(["GOJEK", "SHOPEE"])

    with gojek:
        auth_flow()
        authorization_code_gojek = st.text_input('Masukkan Kode Otorisasi:', '', key='gojek')


    with shopee:
        auth_flow()
        authorization_code_shopee = st.text_input('Masukkan Kode Otorisasi:', '', key='shopee')



    if st.button('Process'):
        with tempfile.TemporaryDirectory() as tmpdirname:
            if (authorization_code_gojek != '') & ('service_gojek' not in locals()):
                service_gojek = authenticate_gmail(authorization_code_gojek)
            if (authorization_code_shopee != '') & ('service_shopee' not in locals()):
                service_shopee = authenticate_gmail(authorization_code_shopee)
            if 'service_gojek' in locals():
                for i, query in enumerate(db['GOFOOD']):
                    messages = list_messages(service_gojek, query + ' smaller:500K')
                    if messages:
                        st.write(f'Found {len(messages)} messages.')
                        for msg in messages[:jumlah]:
                            msg_id = msg['id']
                            save_attachment(service_gojek, msg_id, store_dir=f'{tmpdirname}/downloads/{db.loc[i,"CAB"]}')
                    else:
                        st.write('No messages found with the given criteria.')

            if 'service_shopee' in locals():
                for i, query in enumerate(db['SHOPEEFOOD']):
                    messages = list_messages(service_shopee, query + ' smaller:500K')
                    if messages:
                        st.write(f'Found {len(messages)} messages.')
                        for msg in messages[:jumlah]:
                            msg_id = msg['id']
                            save_attachment(service_shopee, msg_id, store_dir=f'{tmpdirname}/downloads/{db.loc[i,"CAB"]}')
                    else:
                        st.write('No messages found with the given criteria.')

                messages = list_messages(service_shopee, 'SHOPEEPAY larger:500K')
                if messages:
                    st.write(f'Found {len(messages)} messages.')
                    for msg in messages[:jumlah]:
                        msg_id = msg['id']
                        save_attachment(service_shopee, msg_id, store_dir=f'{tmpdirname}/downloads/QRIS_SHOPEE/')

            create_zip_from_folder(f'{tmpdirname}/downloads', 'invoice.zip')
            with open('invoice.zip', 'rb') as f:
                st.download_button(
                    label="Download ZIP File",
                    data=f,
                    file_name='invoice.zip',
                    mime="application/zip"
                )

