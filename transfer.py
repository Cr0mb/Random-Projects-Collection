# A Python script that securely uploads all files from a local directory to a remote server via SFTP with a progress bar for each file.

import os
import paramiko
from tqdm import tqdm  # for progress bar

hostname = ''
username = ''
password = ''

local_dir = r'C:\Users'
remote_dir = '/home/user'

def upload_file(sftp, local_file, remote_file):
    file_size = os.path.getsize(local_file)
    progress = tqdm(total=file_size, unit='B', unit_scale=True, desc=os.path.basename(local_file))

    def progress_callback(transferred, total):
        progress.update(transferred - progress.n)  # update by amount transferred since last callback

    # Use SFTP file open + write to use callback
    with open(local_file, 'rb') as f:
        with sftp.file(remote_file, 'wb') as remote_f:
            remote_f.set_pipelined(True)
            while True:
                data = f.read(32768)  # 32 KB chunks
                if not data:
                    break
                remote_f.write(data)
                progress.update(len(data))

    progress.close()

def sftp_upload_dir(sftp, local_path, remote_path):
    try:
        sftp.chdir(remote_path)
    except IOError:
        sftp.mkdir(remote_path)
        sftp.chdir(remote_path)

    for filename in os.listdir(local_path):
        local_file = os.path.join(local_path, filename)
        remote_file = remote_path + '/' + filename

        if os.path.isfile(local_file):
            print(f'Uploading {local_file} to {remote_file}')
            upload_file(sftp, local_file, remote_file)

def main():
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    print(f'Connecting to {hostname}...')
    ssh.connect(hostname=hostname, username=username, password=password)

    sftp = ssh.open_sftp()
    sftp_upload_dir(sftp, local_dir, remote_dir)

    sftp.close()
    ssh.close()
    print('Upload complete.')

if __name__ == '__main__':
    main()
