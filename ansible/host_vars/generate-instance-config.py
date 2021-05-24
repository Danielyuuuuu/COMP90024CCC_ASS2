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

  f.write("  - name: dash website\n")
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

  f.write("\n# Instance\n")
  f.write("instances:\n")
  for i in range(1, number_of_instances + 1):
    f.write("  - name: instance-{}\n".format(i))
    f.write("    volumes: \'vol-{}\'\n".format(i))
  
  f.close()


if __name__ == "__main__":
  main()