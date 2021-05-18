import argparse

def main():
  number_of_instances = int(input ("Number of instances to create: "))
  f = open("mrc.yaml", "w")

  f.write("# Volume\n")
  f.close()

  f = open("mrc.yaml", "a")
  f.write("volumes:\n")
  for i in range(1, number_of_instances + 1):
    f.write("  - vol_name: vol-{}\n".format(i))
    f.write("    vol_size: 100\n")

  f.write("\n# Security group\n")
  f.write("security_groups:\n")
  f.write("  - name: ssh\n")
  f.write("    description: \"Security group for SSH access\"\n")
  f.write("    protocol: tcp\n")
  f.write("    port_range_min: 22\n")
  f.write("    port_range_max: 22\n")
  f.write("    remote_ip_prefix: 0.0.0.0/0\n")

  f.write("  - name: http\n")
  f.write("    description: \"Security group for HTTP\"\n")
  f.write("    protocol: tcp\n")
  f.write("    port_range_min: 80\n")
  f.write("    port_range_max: 80\n")
  f.write("    remote_ip_prefix: 0.0.0.0/0\n")

  f.write("  - name: https\n")
  f.write("    description: \"Security group for HTTPS\"\n")
  f.write("    protocol: tcp\n")
  f.write("    port_range_min: 443\n")
  f.write("    port_range_max: 443\n")
  f.write("    remote_ip_prefix: 0.0.0.0/0\n")

  f.write("  - name: Dash website\n")
  f.write("    description: \"Security group for dash website\"\n")
  f.write("    protocol: tcp\n")
  f.write("    port_range_min: 5000\n")
  f.write("    port_range_max: 5000\n")
  f.write("    remote_ip_prefix: 0.0.0.0/0\n")

  f.write("  - name: couchDB\n")
  f.write("    description: \"Security group for couchDB\"\n")
  f.write("    protocol: tcp\n")
  f.write("    port_range_min: 5984\n")
  f.write("    port_range_max: 5984\n")
  f.write("    remote_ip_prefix: 0.0.0.0/0\n")

  f.write("  - name: couchDB cluster communication\n")
  f.write("    description: \"Security group for couchDB cluster communication\"\n")
  f.write("    protocol: tcp\n")
  f.write("    port_range_min: 4369\n")
  f.write("    port_range_max: 4369\n")
  f.write("    remote_ip_prefix: 0.0.0.0/0\n")

  f.write("\n# Instance\n")
  f.write("instances:\n")
  for i in range(1, number_of_instances + 1):
    f.write("  - name: testInstance-{}\n".format(i))
    f.write("    volumes: \'vol-{}\'\n".format(i))
  
  f.close()







  
  # with open("mrc.yaml", 'w') as f:
  #   print("# Volume", f=f)
  #   print("volumes:", f=f)
  #   for i in range(1, numberOfInstances + 1):
  #     print("  - vol_name: vol-{}".format(i), f=f)
  #     print("    vol_size: 100", f=f)

  #   print("# Security group", f=f)
  #   print("security_groups:", f=f)
  #   print("  - name: ssh", f=f)
  #   print("    description: \"Security group for SSH access\"", f=f)
  #   print("    protocol: tcp", f=f)
  #   print("    port_range_min: 22", f=f)
  #   print("    port_range_max: 22", f=f)
  #   print("    remote_ip_prefix: 0.0.0.0/0", f=f)

  #   print("  - name: http", f=f)
  #   print("    description: \"Security group for HTTP\"", f=f)
  #   print("    protocol: tcp", f=f)
  #   print("    port_range_min: 80", f=f)
  #   print("    port_range_max: 80", f=f)
  #   print("    remote_ip_prefix: 0.0.0.0/0", f=f)

  #   print("  - name: https", f=f)
  #   print("    description: \"Security group for HTTPS\"", f=f)
  #   print("    protocol: tcp", f=f)
  #   print("    port_range_min: 443", f=f)
  #   print("    port_range_max: 443", f=f)
  #   print("    remote_ip_prefix: 0.0.0.0/0", f=f)

  #   print("  - name: dash website", f=f)
  #   print("    description: \"Security group for dash website"\"", f=f)
  #   print("    protocol: tcp", f=f)
  #   print("    port_range_min: 5000", f=f)
  #   print("    port_range_max: 5000", f=f)
  #   print("    remote_ip_prefix: 0.0.0.0/0", f=f)

  #   print("  - name: couchDB", f=f)
  #   print("    description: \"Security group for couchDB"\"", f=f)
  #   print("    protocol: tcp", f=f)
  #   print("    port_range_min: 5984", f=f)
  #   print("    port_range_max: 5984", f=f)
  #   print("    remote_ip_prefix: 0.0.0.0/0", f=f)

  #   print("  - name: couchDB cluster communication", f=f)
  #   print("    description: \"Security group for couchDB cluster communication"\"", f=f)
  #   print("    protocol: tcp", f=f)
  #   print("    port_range_min: 4369", f=f)
  #   print("    port_range_max: 4369", f=f)
  #   print("    remote_ip_prefix: 0.0.0.0/0", f=f)

  #   print("# Instance", f=f)
  #   print("instances:", f=f)
  #   for i in range(1, numberOfInstances + 1):
  #     print("  - name: testInstance-{}".format(i), f=f)
  #     print("  volumes: \'vol-{}\'".format(i), f=f)


if __name__ == "__main__":
  main()