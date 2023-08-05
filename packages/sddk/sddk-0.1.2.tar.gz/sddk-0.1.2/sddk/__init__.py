import requests
import getpass

def configure_session_and_url(shared_folder_name=None, owner=None): ### insert group folder name or leave empty for personal root
  '''
  interactively setup your sciencedata.dk homeurl, username and password
  in the case of shared folder, inquire for its owner as well
  check functionality and redirections
  '''
  ### set username and password
  username = input("sciencedata.dk username (format '123456@au.dk'): ")
  password = getpass.getpass("sciencedata.dk password: ")
  ### establish a request session
  s = requests.Session()
  s.auth = (username, password)
  sciencedata_homeurl_alternatives = ["https://sciencedata.dk/","https://silo1.sciencedata.dk/","https://silo2.sciencedata.dk/","https://silo3.sciencedata.dk/","https://silo4.sciencedata.dk/"]
  for sciencedata_homeurl_root in sciencedata_homeurl_alternatives:
    if s.get(sciencedata_homeurl_root + "files/").ok:
      root_folder_url = sciencedata_homeurl_root + "files/"
      ### SETTING FOR SHARED FOLDER - if their name is passed in: 
      if shared_folder_name != None:
        shared_folder_owner_url = root_folder_url + shared_folder_name + "/"
        if s.get(shared_folder_owner_url).ok: ### if you are owner of the shared folder 
          root_folder_url = shared_folder_owner_url ### use the url as the endpoint
          print("connection with shared folder established with you as its owner")
        else: # otherwise use endpoint for "shared with me"
          if owner==None:
            owner = input("\"" + shared_folder_name + "\" owner's username: ") ### in the case Vojtech is folder owner
          shared_folder_member_url = sciencedata_homeurl_root + "sharingin/" + owner + "/" + shared_folder_name + "/" 
          try:
            redirection = s.get(shared_folder_member_url, allow_redirects=False).headers["Location"]
            if redirection != None:
              shared_folder_member_url = redirection + "/"
          except:
            pass
          if s.get(shared_folder_member_url).ok:
            root_folder_url = shared_folder_member_url
            print("connection with shared folder established with you as its ordinary user")
          else:
            print("connection with shared folder failed")
    break
  print("endpoint variable has been configured to: " + root_folder_url)
  return s, root_folder_url
