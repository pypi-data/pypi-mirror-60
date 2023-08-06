#  Trello importer
 The package help to get waypoint name of your mission from https://f4.intek.edu.vn/ and import to trello 
#### Requirements:
    Os:Macos, Linux
    You should have install geckodriver
    Macos : brew install geckodriver
    Linux :
    
    
#### Install:
    $pip install trello-importer
    $python3

    >>> from trello_importer.Waypoint_Parser import Parser
    >>> geckgodriver = '/usr/bin/geckodriver'
    >>> driver = webdriver.Firefox(executable_path = geckgodriver)
    
    >>> find_data = Parser("https://f4.intek.edu.vn/login/index.php", "QR Code Reader")
    >>> driver,list_waypoint = find_data.find_html_text(driver,"email_name","email_password")
    
    >>> #find_data.read_data_index() -- use to check data in list
    >>> #find_data.remove_line(3) -- rm data in list at line number with info read_data_index()
    find_data.add_to_trello("https://trello.com/login",driver,list_waypoint)

      
## Contributing
    Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
## License
    This project is licensed under the MIT License - see the LICENSE.md file for details