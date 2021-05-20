import random

def main():
  num_for_crawler = int(input ("Number of hosts for crawler: "))
  num_for_frontend = int(input ("Number of hosts for frontend: "))
  num_for_backend = int(input ("Number of hosts for backend: "))

  hosts = []
  f = open("hosts_backup_file.ini", "r")

  for line in f.readlines():
    line = line.strip()

    if (line != "[instances]"):
      hosts.append(line)
    
  if (num_for_crawler > len(hosts)):
    print("Exception: Do not have enough hosts to run {} crawler program".format(num_for_crawler))
    exit()
  if (num_for_frontend > len(hosts)):
    print("Exception: Do not have enough hosts to run {} frontend".format(num_for_frontend))
    exit()
  if (num_for_backend > len(hosts)):
    print("Exception: Do not have enough hosts to run {} backend".format(num_for_backend))
    exit()

  assigned_hosts = []


  f = open("hosts.ini", "w")

  f.write("[instances]\n")
  f.close()

  f = open("hosts.ini", "a")

  for host in hosts:
    f.write(host + "\n") 

  f.write("\n[crawler]\n") 

  for i in range(0, num_for_crawler):
    f.write(hosts[i] + "\n")
    assigned_hosts.append(hosts[i])
  
  f.write("\n[frontend]\n") 

  for i in range(0, num_for_frontend):
    f.write(hosts[::-1][i] + "\n")
    assigned_hosts.append(hosts[::-1][i])

  f.write("\n[backend]\n") 
  hosts_for_backend = []

  if len(hosts) > len(assigned_hosts):
    for host in hosts:
      if num_for_backend > len(hosts_for_backend):
        if host not in assigned_hosts and host not in hosts_for_backend:
          hosts_for_backend.append(host)
      else:
        break

  while num_for_backend > len(hosts_for_backend):
    host = random.choice(hosts)
    if host not in hosts_for_backend:
      hosts_for_backend.append(host)

  for host in hosts_for_backend:
    f.write(host + "\n")

  f.write("\n[database]\n") 
  if len(hosts) > len(assigned_hosts):
    for host in hosts:
      if host not in assigned_hosts:
        f.write(host + "\n")
  else:
    f.write(random.choice(hosts) + "\n")


  
  # print(hosts)


if __name__ == "__main__":
  main()