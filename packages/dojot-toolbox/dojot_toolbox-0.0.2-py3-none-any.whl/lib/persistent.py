class Persistent:
    def ask_persistence_volume(self, component):
        res = input("Do you want to use persistent volume for {} ? (y/n) [n] ".format( component ))
        return True if res == "y" else False

    def ask_volume_size(self, component, use, default=10):
        if use:
            try:
                return int(input("What is the volume size in GB for {}? [{}] ".format( component, default )))
            except:
                return default 
        return default  