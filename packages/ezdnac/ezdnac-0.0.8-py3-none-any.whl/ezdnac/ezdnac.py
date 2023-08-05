import requests
import warnings
import yaml
import json
import re

warnings.filterwarnings('ignore', message='Unverified HTTPS request')
authToken = None
timeout = None
baseurl = '/api/v1/'
authbaseurl = '/api/system/v1/'

class apic():
	def __init__(self, ip, uid, pw, **kwargs):
		global timeout
		global authToken
		self.ip = ip
		self.uid = uid
		self.pw = pw
		print ("Initializing dnac with ip: " + self.ip)

		#Setting possible keyword adguments:
		try:
			self.port = kwargs['port']
		except:
			self.port = "443"
		
		if timeout == None:
			try:
				timeout = kwargs['timeout']
				self.timeout = timeout
			except:
				timeout = 5
				self.timeout = timeout
			else:
				pass
		
		if authToken == None:
			#Authenticate and retreive an authToken
			AuthURL = "https://" + self.ip + ":" + self.port + authbaseurl + "auth/token"
			payload = {}
			headers = {
			}
			try:
				print ("Authenticating...")
				response = requests.request("POST", AuthURL, headers=headers, data=payload, verify=False, auth=(self.uid, self.pw), timeout=timeout)
			except :
				print("Error: Timeout connection to DNA-C. Most likely a network reachability issue")
				exit()
			data = json.loads(response.text)
			authToken = (data['Token'])	
			self.authToken = authToken
		else:
			#print ("Reusing existing key..")
			self.authToken = authToken

	#Get the selected device ID from serial:
	def getAllDevices(self):
		url = "https://" + self.ip + ":" + self.port + baseurl + "network-device/"
		payload = {}
		headers = {
		'x-auth-token': self.authToken
		}
		response = requests.request("GET", url, headers=headers, data = payload, verify=False, timeout=timeout)
		data = json.loads(response.text)	
		return data

	def id_from_serial(self, serialNumber):
		switches = self.getAllDevices()
		for switch in switches['response']:
			if switch['serialNumber'] == serialNumber:
				switchId = switch['id']
		try:
			return switchId
		except KeyError:
			return None

	def getTemplateId(self, templateName):
		url = "https://" + self.ip + ":" + self.port + baseurl + "template-programmer/project"
		payload = {}
		headers = {
		'x-auth-token': self.authToken
		}
		response = requests.request("GET", url, headers=headers, data = payload, verify=False, timeout=timeout)
		data = json.loads(response.text)	
		

		for projects in data:
			for template in projects['templates']:

				if template['name'] == templateName:
					try:
						templateId = template['id']
						return templateId
					except:
						return None
				else:
					return None

	def getSites(self, **kwargs):
		try:
			searchsite=kwargs['site']
		except:
			searchsite=None
		if searchsite == None:
			url = "https://" + self.ip + ":" + self.port + "/dna/intent/api/v1/site"
		else:
			url = "https://" + self.ip + ":" + self.port + "/dna/intent/api/v1/site?name=" + searchsite + ""
		
		print (url)
		payload = {}
		headers = {
		'x-auth-token': self.authToken,
		'Content-Type': 'application/json',
		'__runsync': 'true',
		'__timeout': '10',
		'__persistbapioutput': 'true',
		}
		response = requests.request("GET", url, headers=headers, data = payload, verify=False, timeout=timeout)
		data = json.loads(response.text)
		return data['response']



#When initialized, populate device parameters:
#Retreive switchId based on serialnumber
class device():
	def __init__(self, dna, **kwargs):
		self.authToken = dna.authToken
		self.dnacIP = dna.ip
		self.port = dna.port
		self.uid = dna.uid
		self.pw = dna.pw
		self.dnac = apic(self.dnacIP, self.uid, self.pw)
		try:
			self.id = kwargs['id']
			print ("Initializing device with id: " + self.id)
		except KeyError:
			self.serialNumber = kwargs['sn']
			print ("Initializing device with serial: " + self.serialNumber)
			try:
				self.id = self.dnac.id_from_serial(self.serialNumber)
			except:
				raise CiscoException('Device not found!')


		#Poll DNA-C API for more details based on the deviceID:
		url = "https://" + self.dnac.ip + ":" + self.dnac.port + baseurl + "network-device/" + self.id

		payload = {}
		headers = {
		'x-auth-token': self.authToken
		}
		try:
			response = requests.request("GET", url, headers=headers, data = payload, verify=False, timeout =2)
			data = json.loads(response.text)
			#Populate the device class:
			self.hostname = data['response']['hostname']
			self.platform = data['response']['platformId']
			self.softwareVersion = data['response']['softwareVersion']
			self.softwareType = data['response']['softwareType']
			self.ip = data['response']['managementIpAddress']
		except:
			raise CiscoException('Something f*!#ed up!')
			exit()


	def getTopology(self):
		ret = []
		url = "https://" + self.dnac.ip + ":" + self.dnac.port + baseurl + "topology/physical-topology/"
		payload = {}
		headers = {
		'x-auth-token': self.authToken
		}
		
		response = requests.request("GET", url, headers=headers, data = payload, verify=False, timeout=timeout)
		data = json.loads(response.text)
		connections = {}
		links = []
		for link in data['response']['links']:
		
			try:
				connections['sourcenode'] = link['source']
				connections['remotenode'] = link['target']
				connections['sourceif'] = link['startPortName']
				connections['remoteif'] = link['endPortName']
				links.append(dict(connections))
			except:
				pass
		ret = links
		return ret


	def getConnections(self):
		ret = []
		url = "https://" + self.dnac.ip + ":" + self.dnac.port + baseurl + "topology/physical-topology/"
		payload = {}
		headers = {
		'x-auth-token': self.authToken
		}
		response = requests.request("GET", url, headers=headers, data = payload, verify=False)
		data = json.loads(response.text)
		connections = {}
		links = []
		for link in data['response']['links']:
			try:
				if link['source'] == self.id:
					connections['remotenode'] = link['target']
					connections['remoteif'] = link['endPortName']
					connections['localif'] = link['startPortName']
					links.append(dict(connections))
				elif link['target'] == self.id:
					connections['remotenode'] = link['source']
					connections['remoteif'] = link['startPortName']
					connections['localif'] = link['endPortName']
					links.append(dict(connections))
			except:
				pass
		ret = links
		return ret


	def deployTemplate(self, templateId, templateParams):
			url = "https://" + self.dnac.ip + ":" + self.dnac.port + baseurl + "template-programmer/template/deploy"
			payload = {
			  "templateId": templateId,
			   "targetInfo": [
			     {
			      "id": self.id,
			      "type": "MANAGED_DEVICE_UUID",
				  "params": templateParams
			     }
				]}
			
			headers = {
			  'x-auth-token': self.authToken,
			  'Content-Type': 'application/json',
			}

			response = requests.request("POST", url, headers=headers, json=payload, verify=False, timeout=10)

			if response.status_code == 202:
				return "Template Deployed!"
			else:
				return "Error deploying template:" + str(response.text.encode('utf8'))


	def findNextPortchannel(self):
		url = "https://" + self.dnac.ip + ":" + self.dnac.port + baseurl + "interface/network-device/" + self.id
		payload = {}
		headers = {
			  'x-auth-token': self.authToken,
			  'Content-Type': 'application/json',
			}
		response = requests.request("GET", url, headers=headers, json=payload, verify=False, timeout=5)
		config = json.loads(response.text)

		existing_ids = []
		for interface in config['response']:
			if re.match(r'Port-channel.*', str(interface['portName'])):
				intf = int(str(interface['portName']).strip("'Port-channel"))
				existing_ids.append(intf)
					
		for i in range(1,49):
			if (i) not in existing_ids:
				next_id = i
				break
		return next_id
		
	def assignToSite(self, siteId):
		url = "https://" + self.dnac.ip + ":" + self.port + "/dna/system/api/v1/site/" + siteId + "/device"
		payload = {
		  "device": [
		    {
		      "ip": self.ip
		    }
		  ]
		}
		print (payload)
		headers = {
		'x-auth-token': self.authToken,
		'Content-Type': 'application/json',
		'__runsync': 'true',
		'__timeout': '10',
		'__persistbapioutput': 'true',
		}
		response = requests.request("POST", url, headers=headers, json=payload, verify=False, timeout=timeout)
		#data = json.loads(response.text)
		return response.text


	def claimDevice(self):
		
		
		data = "stuff"	
		
		return data


	def getNeighbors(self):
		connections = self.getConnections()
		neighbors = []
		for link in connections:
			if link['remotenode'] in neighbors:
				continue
			else:
				neighbors.append(link['remotenode'])
		return neighbors


	#return every interface connected to us from specific neighbor
	def getNeighborIfs(self, neighbor):
		connections = self.getConnections()
		interfaces = []
		for link in connections:
			if link['remotenode'] == neighbor:
				interfaces.append(link['remoteif'])
		return interfaces


	def getModules(self):
		url = "https://" + self.dnac.ip + ":" + self.port + baseurl + "network-device/module?deviceId=" + self.id
		payload = {}
		headers = {
		'x-auth-token': authToken
		}
		response = requests.request("GET", url, headers=headers, data = payload, verify=False)
		data = json.loads(response.text)
		modules = data['response']

		self.modules = modules
		
		switches = []
		for module in modules:
				name = module['name']
				switch = str((re.findall(r'Switch \d', name))).strip("[']")
				switches.append(switch)
		self.stackcount = len((set(switches)))
		
		return modules

class CiscoException(Exception):
    pass



#####################################################
## Written by Johan Lahti, CCIE60702, Conscia Sweden#
## https://github.com/johan-lahti					#
## shiproute.net 									#
#####################################################