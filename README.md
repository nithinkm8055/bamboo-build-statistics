# Bamboo plan overview
**A simple web application to show overview of all branches in a plan and their build statistics**

# Prerequisites
1. Python3
2. Install all libraries in `requirements.txt` using pip
3. Update all required parameter values in `server_config.py`

# Usage
```sh
python flaskapp.py
```

Running the above command by default runs an application on port 5000 and can be accessed at : http://localhost:5000

The application exposes below 3 apis:

```sh
# check to see the build status for all branches in a plan
http://<server_ip>:<server_port>/plan/<planKey>/allbranches 
```

```sh
# check to see if a branch is onboarded to a plan
http://<server_ip>:<server_port>/plan/<planKey>/branch/<branchname> 
```

```sh
# check to see if a branch is onboarded to a plan
http://<server_ip>:<server_port>/plan/<planKey>/branch/<branchname>/buildstatus
```

# Deploy
* To deploy your app on an apache server using wsgi, refer: https://asdkazmi.medium.com/deploying-flask-app-with-wsgi-and-apache-server-on-ubuntu-20-04-396607e0e40f
* [Apache config](apache_config/flaskapp.conf)

# Notes
* [API Documentation](https://docs.atlassian.com/atlassian-bamboo/REST/6.8.0/)
