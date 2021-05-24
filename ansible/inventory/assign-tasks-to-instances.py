import random

def main():
  num_for_crawler = int(input ("Number of hosts for crawler: "))
  num_for_frontend = int(input ("Number of hosts for frontend: "))
  num_for_dataAnalysis = int(input ("Number of hosts for data analysis: "))

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
  if (num_for_dataAnalysis > len(hosts)):
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

  f.write("\n[dataAnalysis]\n") 
  hosts_for_dataAnalysis = []

  if len(hosts) > len(assigned_hosts):
    for host in hosts:
      if num_for_dataAnalysis > len(hosts_for_dataAnalysis):
        if host not in assigned_hosts and host not in hosts_for_dataAnalysis:
          hosts_for_dataAnalysis.append(host)
      else:
        break

  while num_for_dataAnalysis > len(hosts_for_dataAnalysis):
    host = random.choice(hosts)
    if host not in hosts_for_dataAnalysis:
      hosts_for_dataAnalysis.append(host)

  for host in hosts_for_dataAnalysis:
    f.write(host + "\n")
    if host not in assigned_hosts:
      assigned_hosts.append(host)

  f.write("\n[database]\n") 
  if len(hosts) > len(assigned_hosts):
    for host in hosts:
      if host not in assigned_hosts:
        f.write(host + "\n")
        break
  else:
    f.write(random.choice(hosts) + "\n")




if __name__ == "__main__":
  main()