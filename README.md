# Seekr

## Set up
```
python3 -m venv venv/
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```
select venv python interpreter if using vscode
## Running server
```
python manage.py runserver
```

## Branches 
Create a new branch using 
```
git checkout -b [name of your branch]
```
Pushing and pulling from your branch: 
```
git pull origin [branch]
```
```
git commit [files you want added, if any were created] -m [message]
git push origin [branch]
```

###### Some general rules to follow: 
- Don't push directly to the master branch 
- Only work on one task at a time on each branch 
- Request a pull and merge once the task is fully complete and the code has been peer reviewed 
- Only merge to master branch after code review from peers 
- Always put meaningful commit messages 