import json
import sys
import os
import boto3
import random
import string
import urllib.request as urllib2
import urllib
import math
import zipfile
import subprocess
from botocore.exceptions import ClientError

def lambda_handler(event, context):
    # Initialise the required variables
    client = boto3.client(
        'lambda',
        aws_access_key_id = event["queryStringParameters"]['aws_access_key_id'],
        aws_secret_access_key = event["queryStringParameters"]['aws_secret_access_secret'],
        region_name = event["queryStringParameters"]['region_name'],
    )
    
    path  = "/tmp/project" 
    repo = event["queryStringParameters"]['github_repo_path']
    clone = "git clone https://"+ event["queryStringParameters"]['github_repo_path'] +" /tmp/project" 
    accessemail = "git config user.email '" + event["queryStringParameters"]['github_access_email'] + "'"
    accessusername = "git config user.name '" + event["queryStringParameters"]['github_access_name'] + "'"
    add = "git add ."
    commit = "git commit . -m 'auto-commit'"
    origin = "https://" + event["queryStringParameters"]['github_access_name'] + ":" + event["queryStringParameters"]['github_secret'] + "@" + repo
    push = "git push " + origin + " main"
    
    # Check-in lambda function 
    if (event["queryStringParameters"]['action'] == 'checkin'):
        try:
            functions = client.list_functions()
            
            functionDetails = client.get_function(
                FunctionName=event["queryStringParameters"]['function_name'],
            )
            
            if ('Code' in functionDetails):
                downloadSource(functionDetails['Code']['Location'])
                    
                os.system('rm -rf ' + path)
                os.mkdir(path)
                os.chdir(path) # Specifying the path where the cloned project needs to be copied
                os.system(clone) # Cloning
                
                with zipfile.ZipFile("/tmp/sample.zip", 'r') as zip_ref:
                    zip_ref.extractall(path)
                
                files = os.listdir("/tmp/")
                            
                for filename in files:
                    print(filename)
                    
                os.system(accessemail)
                os.system(accessusername)
                os.system(add)
                commitMessage = subprocess.getoutput(commit)
                pushMessage = subprocess.getoutput(push)
                response = {'commit': commitMessage, 'push': pushMessage}
            else:
                response = {'error': 'Function ' + event["queryStringParameters"]['function_name'] + ' does not exist'}
        except ClientError as e:
            print(e.response)
            response = {'error': e.response['Error']['Message']}
    else:
        response = {'error': event["queryStringParameters"]['action'] + " is not a valid action"}

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
    
    
def downloadSource(url):
    urllib.request.urlretrieve(url, "/tmp/sample.zip")

def downloadChunks(url):
    """Helper to download large files
        the only arg is a url
       this file will go to a temp directory
       the file will also be downloaded
       in chunks and print out how much remains
    """

    baseFile = os.path.basename(url)

    uuid_path = ''.join([random.choice(string.ascii_letters + string.digits) for i in range(10)])

    #move the file to a more uniq path
    os.umask(0o002)
    temp_path = "/tmp"
    temp_path_uniq = os.path.join(temp_path,uuid_path)
    os.mkdir(temp_path_uniq)

    try:
        file = os.path.join(temp_path_uniq,"baseFile")

        req = urllib2.urlopen(url)
        total_size = 10000 
        #int(req.info().getheader('Content-Length').strip())
        downloaded = 0
        CHUNK = 256 * 10240
        with open(file, 'wb') as fp:
            while True:
                chunk = req.read(CHUNK)
                downloaded += len(chunk)
                # print (math.floor( (downloaded / total_size) * 100 ))
                if not chunk: break
                fp.write(chunk)
    except urllib2.HTTPError as e:
        print ("HTTP Error:",e.code , url)
        return False
    except urllib2.URLError as e:
        print ("URL Error:",e.reason , url)
        return False

    return file
