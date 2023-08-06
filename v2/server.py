from fs_server import FS_Server
import psutil
import socket

def choose_network_interface():
    interfaces = psutil.net_if_addrs()
    
    if not interfaces:
        print("No network interfaces found.")
        return
    
    print("Available network interfaces:")
    for i, interface in enumerate(interfaces.keys(), start=1):
        print(f"{i}. {interface}")
    
    choice = input("Enter the number of the network interface you want to choose: ")
    
    try:
        index = int(choice) - 1
        selected_interface = list(interfaces.keys())[index]
        return selected_interface
    except (ValueError, IndexError):
        print("Invalid choice. Please enter a valid number.")
        return None

def get_ip_address(interface_name):
    interfaces = psutil.net_if_addrs()
    
    if interface_name in interfaces:
        for addr in interfaces[interface_name]:
            if addr.family == socket.AF_INET:
                return addr.address
    else:
        return None


if __name__ == "__main__":
    selected_interface = choose_network_interface()
    if selected_interface:
        ip_address = get_ip_address(selected_interface)
        if ip_address:
            print(f"IP address of {selected_interface}: {ip_address}")
        else:
            print(f"No IPv4 address found for {selected_interface}.")
    else:
        print("No network interface selected.")
    
    if ip_address is None:
        exit()
    
    server = FS_Server((ip_address, 9999))
    server.start_server()
