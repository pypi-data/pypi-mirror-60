import requests
import warnings
import json
import re

warnings.filterwarnings('ignore', message='Unverified HTTPS request')
authToken = None
timeout = None
verifySSL = False
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
		
		try:
			self.verifySSL = False
			verifySSL = kwargs['verifySSL']
		except:
			self.verifySSL = False
			verifySSL = False

		if timeout == None:
			try:
				timeout = kwargs['timeout']
				self.timeout = timeout
			except:
				timeout = 10
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
				response = requests.request("POST", AuthURL, headers=headers, data=payload, verify=verifySSL, auth=(self.uid, self.pw), timeout=timeout)
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
			for templates in projects['templates']:
				try:
					if templates['name'] == templateName:
						return (templates['id'])
				except:
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
		
		payload = {}
		headers = {
		'x-auth-token': self.authToken,
		'Content-Type': 'application/json',
		'__runsync': 'true',
		'__timeout': '10',
		'__persistbapioutput': 'true',
		}
		response = requests.request("GET", url, headers=headers, data=payload, verify=False, timeout=timeout)
		data = json.loads(response.text)

		if searchsite != None:		
			for site in data['response']:
				return site['id']

		return data['response']
		


	def getPnpDevices(self, **kwargs):
		try:
			serialNumber = kwargs['sn']
		except:
			serialNumber = None
		url = "https://" + self.ip + ":" + self.port + "/dna/intent/api/v1/onboarding/pnp-device"
		payload = {}
		headers = {
		'x-auth-token': self.authToken
		}
		response = requests.request("GET", url, headers=headers, data=payload, verify=False, timeout=timeout)
		data = json.loads(response.text)

		if serialNumber == None:
			return data
		else:
			for device in data:
				if device['deviceInfo']['serialNumber'] == serialNumber:
					ret = device

			try:
				return device
			except:
				raise ezDNACError('Device with serial number' + serialNumber + ' not found in pnp.')





	def getInventoryDevies(self, **kwargs):
		try:
			serialNumber = kwargs['sn']
		except:
			serialNumber = None
		try:
			deviceId = kwargs['id']
		except:
			deviceId = None

		if deviceId != None:
			url = "https://" + self.ip + ":" + self.port + baseurl + "network-device/" + deviceId
		else:
			url = "https://" + self.ip + ":" + self.port + baseurl + "network-device/"

		payload = {}
		headers = {
		'x-auth-token': self.authToken
		}
		response = requests.request("GET", url, headers=headers, data = payload, verify=False, timeout=timeout)
		data = json.loads(response.text)	
		
		if deviceId != None:
			return data['response']
		else:
			if serialNumber == None:
				return data['response']
			else:
				for device in data['response']:
					if device['serialNumber'] == serialNumber:
						return device



#When initialized, populate device parameters:
#Retreive switchId based on serialnumber
class device():
	def __init__(self, dna, **kwargs):
		self.authToken = dna.authToken
		self.dnacIP = dna.ip
		self.port = dna.port
		self.uid = dna.uid
		self.pw = dna.pw
		self.state = ""
		self.dnac = apic(self.dnacIP, self.uid, self.pw)
		try:
			self.id = kwargs['id']
			self.initMethod = 'id'
		except:
			self.serialNumber = kwargs['sn']
			self.initMethod = 'sn'

		#if init method is id, the device must be in inventory. Populate all attributes:		
		if self.initMethod == 'id':
			try:
				self.state 			= "Provisioned"
				self.serialNumber 	= self.dnac.getInventoryDevies(id=self.id)['serialNumber']
				self.hostname		= self.dnac.getInventoryDevies(id=self.id)['hostname']
				self.platform		= self.dnac.getInventoryDevies(id=self.id)['platformId']
				self.softwareVersion= self.dnac.getInventoryDevies(id=self.id)['softwareVersion']
				self.softwareType	= self.dnac.getInventoryDevies(id=self.id)['softwareType'] 
			except:
				raise ezDNACError('device with id' + self.id +' not found')
		#if method is sn, the device can be either in inventory or pnp, have to try both
		elif self.initMethod == 'sn':
			#Try populate the attributes via the inventory:
			try:
				INVdevices 			= self.dnac.getInventoryDevies(sn=self.serialNumber)
				self.id 			= INVdevices['id']
				self.hostname		= INVdevices['hostname']
				self.platform		= INVdevices['platformId']
				self.softwareVersion= INVdevices['softwareVersion']
				self.softwareType	= INVdevices['softwareType']
				self.state 			= "Provisioned"
			except:
				pass
			if self.state != "Provisioned":
				try:
				#Otherwise try populate attributes via pnp:
					PNPdevices 			= self.dnac.getPnpDevices(sn=self.serialNumber)
					self.id 			= PNPdevices['id']
					self.state  		= PNPdevices['deviceInfo']['state']
					self.hostname		= PNPdevices['deviceInfo']['name']
					self.platform		= PNPdevices['deviceInfo']['pid']
					self.softwareVersion= PNPdevices['deviceInfo']['imageVersion']
					self.softwareType	= PNPdevices['deviceInfo']['agentType'] 
				except:
					raise ezDNACError('device with serialNumber' + self.serialNumber +' not found')

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
					print ("source")
					connections['remotenode'] = link['target']
					connections['remoteif'] = link['endPortName']
					connections['localif'] = link['startPortName']
					links.append(dict(connections))
				elif link['target'] == self.id:
					print ("arget")
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
				try:
					#Försök nyckla ut deploymentId som respons. API responsen är trasig så får köra regex
					result = json.loads(response.text)['deploymentId']
					deploymentId = (str(re.findall(r'Template Deployemnt Id.*', result)).strip("['Template Deployemnt Id: ]"))
					if deploymentId == "":
						self.deploymentId = None
						return None
					else:
						self.deploymentId = deploymentId
						return {"deploymentId":deploymentId}
				except:
					return None

	def deployTemplateStatus(self, **kwargs):
		try:
			self.deploymentId = kwargs['id']
		except:
			pass
		url = "https://" + self.dnac.ip + ":" + self.dnac.port + "/dna/intent/api/v1/template-programmer/template/deploy/status/" + self.deploymentId
		payload = {}
		headers = {
		'x-auth-token': self.authToken,
		'Content-Type': 'application/json',
		}
		response = requests.request("GET", url, headers=headers, json=payload, verify=False, timeout=timeout)

		data = json.loads(response.text)
		return data['status']



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

	def claimDevice(self, siteId, **kwargs):
		url = "https://" + self.dnac.ip + ":" + self.port + "/api/v1/onboarding/pnp-device/site-claim"
		try:
			payload = {
		    "siteId": siteId,
		     "deviceId": pnpDeviceId,
		     "type": "Default",
		     "imageInfo": {"imageId": "None", "skip": true},
		     "configInfo": {"configId": kwargs['templateId'], "configParameters":[kwargs[params]]}
			}
		except:
			payload = {
	        "siteId": siteId,
	         "deviceId": self.id,
	         "type": "Default",
	         "imageInfo": {"imageId": "None", "skip": "true"},
	         "configInfo": {"configId": "", "configParameters":[]}
			}

		headers = {
		'x-auth-token': authToken,
		'Content-Type': 'application/json',
		}
		response = requests.request("POST", url, headers=headers, json=payload, verify=False, timeout=timeout)
		data = json.loads(response.text)
		return data

class ezDNACError(Exception):
    pass



#####################################################
## Written by Johan Lahti, CCIE60702				#
## https://github.com/johan-lahti					#
## shiproute.net 									#
#####################################################