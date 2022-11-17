# Set options for certfile, ip, password, and toggle off
# browser auto-opening
c.NotebookApp.certfile = u'{{ ansible_env.HOME }}/.jupyter/jupyter.pem'
c.NotebookApp.keyfile = u'{{ ansible_env.HOME }}/.jupyter/jupyter.key'
c.NotebookApp.password = u'{{ jupyter_notebook_pass }}'
# Set ip to '*' to bind on all interfaces (ips) for the public server
c.NotebookApp.ip = '*'
c.NotebookApp.open_browser = False
c.NotebookApp.notebook_dir = u'{{ ansible_env.HOME }}/notebooks'
c.Spawner.default_url = '/lab'
c.NotebookApp.port = 8888
