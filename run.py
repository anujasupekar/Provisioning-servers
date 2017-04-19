import boto.ec2
import time
import digitalocean


print "Connecting to AWS..."
conn = boto.ec2.connect_to_region("us-west-2",
	aws_access_key_id='[Secret key here]',
	aws_secret_access_key='[Access key here]')

print "Creating AWS reservation"
reservation = conn.run_instances(
		        'ami-e1906781',
		        key_name='[key name]',
		        instance_type='t2.micro',
		        security_groups=['security group name'])

print "Created AWS instance: "
print reservation.instances

instance = reservation.instances[0]
instance.update()
while instance.state == "pending":
	print "Waiting for instance to run..."
	time.sleep(5)
	instance.update()

print "Instance ready"
print "Public IP:"
print instance.ip_address

print "Creating inventory file"
inventory_file = open("inventory", "w")
inventory_file.write("node0 ansible_ssh_host="+instance.ip_address+" ansible_ssh_user=ubuntu ansible_ssh_private_key_file=keypair_name\n")

print
print "Creating digitalocean instance"
manager = digitalocean.Manager(token="token here")
keys = manager.get_all_sshkeys()

droplet = digitalocean.Droplet(token="token here",
	name='Droplet1',
	region='nyc1', 
	image='ubuntu-14-04-x64', # Ubuntu 14.04 x64
	size_slug='512mb', # 512MB
	ssh_keys=keys, 
	backups=False)
droplet.create()

print "Created digitalocean instance: "
print droplet
actions = droplet.get_actions()
action_status = actions[0].status

while action_status == 'in-progress':
	print "Waiting for instance to run..."
	actions = droplet.get_actions()
	for action in actions:
		action.load()
		action_status = action.status
		print action_status
	time.sleep(5)

droplet.load()

print "Instance ready"
print "Public IP:"
print droplet.ip_address

print "Appending row to inventory file"
inventory_file.write("node1 ansible_ssh_host="+droplet.ip_address+" ansible_ssh_user=root ansible_ssh_private_key_file=key_name\n")
print "Done"