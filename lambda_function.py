import json
import io
import os
import boto3
import random
import string
import urllib.request as urllib2
import urllib
import math
import zipfile
from zipfile import ZipFile
import subprocess
import shutil
from botocore.exceptions import ClientError


def lambda_handler(event, context):
    
    print("Initialising variables")
    
    # initialise input params
    action = event["queryStringParameters"]['action']
    function_name = event["queryStringParameters"]['function_name']
    github_repo_path = event["queryStringParameters"]['github_repo_path']
    github_access_email = event["queryStringParameters"]['github_access_email']
    github_access_name = event["queryStringParameters"]['github_access_name']
    github_secret = event["queryStringParameters"]['github_secret']
    
    # Initialise boto agent
    client = boto3.client(
        'lambda',
        aws_access_key_id = event["queryStringParameters"]['aws_access_key_id'],
        aws_secret_access_key = event["queryStringParameters"]['aws_secret_access_secret'],
        region_name = event["queryStringParameters"]['region_name'],
    )
    
    # initialise git specific commands
    path  = "/tmp/project" 
    repo = github_repo_path
    clone = "git clone https://"+ github_repo_path +" /tmp/project" 
    accessemail = "git config user.email '" + github_access_email + "'"
    accessusername = "git config user.name '" + github_access_name + "'"
    add = "git add ."
    commit = "git commit . -m 'auto-commit'"
    origin = "https://" + github_access_name + ":" + github_secret + "@" + repo
    push = "git push " + origin + " main"
    
    try:
        print("Executing action: " + action)
        
        # Check-in lambda function
        if (action == 'checkin'):
            print("Getting " + function_name + " function details...")
            # Get the function details
            functionDetails = client.get_function(
                FunctionName = function_name,
            )
            
            print("Downloading the function source...")
            # Download the function content 
            downloadSource(functionDetails['Code']['Location'])
                
            print("Cleaning up the path before cloning")
            os.system('rm -rf ' + path)
            os.mkdir(path)
            os.chdir(path) # Specifying the path where the cloned project needs to be copied
            print("Cloning the repo...")
            os.system(clone) # Cloning
            
            print("Extracting the downloaded source to the repo directory...")
            # Extract the downloaded source to the repo directory
            with zipfile.ZipFile("/tmp/sample.zip", 'r') as zip_ref:
                zip_ref.extractall(path)
                
            print("Providing git access permission to the system")
            os.system(accessemail)
            os.system(accessusername)
            os.system(add)
            print("Git commit and push...")
            commitMessage = subprocess.getoutput(commit)
            pushMessage = subprocess.getoutput(push)
            
            response = {'commit': commitMessage, 'push': pushMessage}
            print("response" + response)
            
            
        # Check-out lambda function
        elif (action == 'checkout'):
            print("Cleaning up the path before cloning the repo...")
            os.system('rm -rf ' + path)
            os.mkdir(path)
            os.chdir(path) # Specifying the path where the cloned project needs to be copied
            print("Cloning the repository...")
            os.system(clone) # Cloning
            
            print("Archiving the content of repository to a zip file...")
            buf = io.BytesIO()
            with ZipFile(buf, 'w') as z:
                for full_path, archive_name in files_to_zip(path=path + "/"):
                    z.write(full_path, archive_name)
            
            print("Deploying the lambda function with the new zip file...")
            functionUpdate = client.update_function_code(
                FunctionName = function_name,
                ZipFile=buf.getvalue()
            )
            
            print("Function is updated!")
            
            response = {'message': 'Lambda function: " + function_name + " is deployed'}
            print("response" + response)
            
        else:
            response = {'status': 'failure', 'error': action + " is not a valid action"}
            print("response" + response)
    except ClientError as e:
        print(e.response)
        response = {'status': 'failure', 'error': e.response['Error']['Message']}

    return {
        'statusCode': 200,
        'body': json.dumps(response)
    }
    
def files_to_zip(path):
    for root, dirs, files in os.walk(path):
        for f in files:
            full_path = os.path.join(root, f)
            archive_name = full_path[len(path) + len(os.sep) - 1:]
            yield full_path, archive_name

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
