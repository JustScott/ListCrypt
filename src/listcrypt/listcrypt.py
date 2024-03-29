'''
Cryptographic module that encrypts/decrypts each character of the data
by adding or subtracting the integer equivalent of that character 
against the integer equiavalent of each each character in your key. 

The key is converted to a sha256 hash and used to create more key
hashes to match and slightly exceed the length of the data.

'''

import hashlib
import base64
import ast
from multiprocessing import Process, Manager, cpu_count
import math
import platform


#Defining functions before iterative use to increase efficiency
chr_ = chr
ord_ = ord


def sha256(data:str) -> str:
    '''
    Returns the Hashed Value of your data

    Args:
        data (str): Any String Value Will Work

    Returns:
        str: The Hashed Value of The Data
    '''
    return base64.b64encode(hashlib.sha256(data.encode()).digest()).decode()


def data_verification(key:str, data:str) -> bool:
    '''
    Verifies the data will be encrypted and decrypted without 
    error by testing a small chunck of said data, returning true
    if the origional chunk of data matches the decrypted 
    version of the same data

    Args:
        key (str):
            The key used to encrypt the data

        data (str or bytes):
            The data that will be encrypted

    Returns:
        bool:
            This will return true if the data was encrypted and 
            decrypted without error, otherwise it will return False
    '''

    # Finds the center of the data and takes the following
    # ten characters to encrypt/decrypt
    size = len(data)/2
    sample_data = data[round(size):round(size+10)]

    encrypted_data = encrypt(key, sample_data)
   
    decrypted_data = decrypt(key, encrypted_data)

    # Returns true if the origional chunck of data matches
    # the decrypted version of the data
    return sample_data == decrypted_data


def convert_data(key:str, data:'any data type') -> list:
    '''
    Converts the data to a string format for encryption

    Args:
        key (str):
            The key used to encrypt the data

        data ('any data type'):
            The data that will be encrypted

    Returns:
        list:
            [0]: The new 'str' version of the data
            [1]: The origional type of the data, for converting
                 back later
    '''
    # This block of code converts the data to a str,
    # no matter the origional type
    if type(data) == str:
        return data, 'str'
    if type(data) == bytes:
        try:
            data = data.decode('utf-8')
            if data_verification(key, data) and type(data) == str:
                return data, 'utf-8'
        except Exception:
            try:
                #Common way of decoding certain image files
                data = base64.b64encode(data).decode()
                if data_verification(key, data) and type(data) == str:
                    return data, 'base64'
            except:
                data = data.decode('ISO-8859-1')
                if data_verification(key, data) and type(data) == str:
                    return data, 'ISO-8859-1'
    if type(data) != (str or bytes):
        return str(data), 'ast'


def convert_data_back(metadata: list) -> 'any data type':
    '''
    Converts the data back to its origional type as given by
    the 'origional_data_type' parameter in the 'metadata' list.
    
    This is built to work seamlessly with the 'convert_data' function.


    Args:
        metadata (list):
            data (str):
                This is the data variable returned
                the 'convert_data' function that will
                be converted back to the 'origional_data_type'

            origional_data_type (str):
                The type returned by the 'convert_data' function,
                used to return the str 'data' back to its origional type

    Returns:
        any data type:
            The origional data before being ran through
            any conversion functions

    '''
    data = metadata[0]
    origional_data_type = metadata[1]

    #Converting the data back to whatever type is given by the 
    # 'origional_data_type' argument
    if origional_data_type == 'str':
        return data
    if origional_data_type == 'utf-8':
        return data.encode('utf-8')
    if origional_data_type == 'ast':
        return ast.literal_eval(data)
    if origional_data_type == 'base64':
        return base64.decodebytes(data.encode())
    if origional_data_type == 'ISO-8859-1':
        return data.encode('ISO-8859-1')
    

def range_finder(data:str or bytes) -> int:
    '''
    Finds the character with the largest integer equivalent in your data

    Args:
        data (str or bytes):
            The data to be used for encryption/decryption

    Returns:
        int: The largest integer equivalent character of the data

    '''
    if type(data) == str:
        data = data.encode()

    # Adding 1 to prevent future mathematical errors during decryption
    max_range = max(data)+1

    # Increase to atleast 130 to ensure complexity of encrypted data
    if max_range < 130:
        max_range += 130-max_range

    return max_range


def create_key(key:str, data_length:int) -> bytes:
    '''
    Uses the sha256 hash of the 'key' parameter to create and 
    concatenate more keys (based upon the origional) to a new 
    key variable that is either the same size as or slighty 
    larger than the length of the data 
   
    Args:
        key (str):
            The key used for encryption and decryption
        data_length (int):
            The length of the data to be encrypted or decrypted

    Returns:
        bytes: The bytes equivalent of the combined keys

    '''

    new_key = ""
    length_of_hash = len(sha256("x"))

    # The number of iterations required to match the length of 
    # 'new_key' and 'data_length'
    required_key_length = math.ceil(data_length/length_of_hash)

    # Puts an integer at the end of the origional key and adds
    # the hash of that to the combined 'new_key' variable
    for i in range(required_key_length+5):
        new_key += sha256(key+str(i))

    return new_key


def segment_data(data:'iterable', segments:int) -> list:
    '''
    Splits the data evenly amongst the amount of 'segments' required

    Args:
        data (any iterable):
            The data to evenly split
        segments (int):
            The amount of splits you want in the data

    Returns:
        list: 
            A list of evenly distributed items from the data
    '''

    # The number of items per segment, if all segments were even
    segment_length_estimate = 1
    data_length_adjustment = 0
    remaining_data_length = 0
    if len(data) > segments:
        segment_length_estimate = int(len(data)/segments)
        data_length_adjustment = -1

        # The remaining items after the segments are all equal in length
        remaining_data_length = len(data)%segments

    # Get all evenly distributed segments
    segmented_data = [
        data[position:position+segment_length_estimate]
        for position in range(0, len(data)+data_length_adjustment, segment_length_estimate)
    ]

    # While there are more segments than specified
    while len(segmented_data) > segments:
        # Remove & return the extra segment
        extra_segment = segmented_data.pop()
        # While there are items in the extra segment
        while len(extra_segment):
            # Loop through each prior segment, and move a single item from the
            # extra segment onto the segments until the extra_segment is empty
            for position in range(0, len(segmented_data)-1):
                # If the extra segment runs out before the loop ends
                if not len(extra_segment):
                    break
                extra_segment_item = extra_segment.pop()
                segmented_data[position].append(extra_segment_item)

    # Eliminite any empty segments
    return list(filter(None, segmented_data))


def pull_metadata(key:str, data:bytes) -> dict:
    '''
    Pulls metadata from the encrypted bytes and puts it in a 
    dictionary for easy readibility and manipulation

    Args:
        data (bytes):
            The ouput of running the encryption function
        key (bytes):
            The key used to encrypt the data            

    Returns:
        dict: A dictionary of the metadata and encrypted data
    '''
    metadata_dictionary = {}
    data = data.decode()

    # Getting the metadata location information
    splitter_chars = key[2:12]
    position = int("".join(list(map(str, map(ord, key)))))%len(data)
    if position >= (len(data)-30):
        position = int(len(data) * .2)

    # Splitting the metadata from the regular data
    metadata = data[position:data.index(splitter_chars)]
    data = data.replace(metadata+splitter_chars, '')

    # Decrypt metadata
    metadata = "".join([chr_((ord_(metadata[pos])-ord_(key[pos]))%130) for pos in range(len(metadata))])

    # Divides the metadata
    metadata_dictionary["type"] = metadata.split('(')[0]

    metadata_dictionary["range"] = int(metadata.split('(')[1].replace(')',''))

    metadata_dictionary["data"] = data
    
    return metadata_dictionary


def encrypt(key:'any data type', data:'any data type', processes=cpu_count()) -> bytes:
    '''
    Encrypts the data by adding each characters integer equivalent to the 
    integer equivalent of the character in the same position in the new key 
    variable generated by the 'key parameter'

    Args:
        key (any data type):
            Used to create a larger key which is used for encrypting the data 
        data (any data type):
            The data to be encrypted
        processes (int, default:All available CPU cores):
            The amount of processes allowed to run simultaneously,
            the more allowed, the faster the decryption.
            ( Multi-cored encryption only currently available on
            linux )

    Returns:
        bytes: The encrypted data, along with metadata for decrypting the data
    
    '''
    # ListCrypt currently does not support multiprocessing in windows
    if platform.system() != "Linux":
        processes = 1

    # Finds the origional type of the data for converting back to
    # after decryption
    data,data_type = convert_data(key, data)
    metadata = data_type

    # Puts a random string at the start of the data before encryption
    # to verify no data corruption during decryption
    confirmation_data = "39"
    data = confirmation_data+data

    # Finds the max range of the data according to 
    # each characters ord() equivalent
    max_range = range_finder(data)
    metadata += f"({max_range})"

    metadata_key = key
    # Creates a new, longer key from the origional 'key' variable
    # to match or exceed the length of the data
    key = create_key(str(key), len(data))

    # Creates a dictionary that is shared across independent processes
    shared_dictionary = Manager().dict()

    # Splits the data into segments for even distribution
    # across CPU cores
    segments = processes
    segmented_data = segment_data(data, segments)
    segmented_key = segment_data(key, segments)

    # Cleaning up memory
    data=None

    # Leaving out the first segment for the main process to run after
    # it starts the child processes
    child_segmented_data = segmented_data[1:]
    child_segmented_key = segmented_key[1:]

    def multiprocess_encryption(key:str, data:str, segment:int, shared_dictionary:dict) -> bool:
        '''
        Takes chuncks of data and adds them to a shared dictionary,
        with the keys being the segments origional position for concatenation
        after encryption

        Args:
            data (str):
                The string of data to be encrypted
            segment (int):
                The origional location of the data in the list variable
                'segmented_data', so it can be concatenated back into the
                correct order from the dictionary
            shared_dictionary (dict):
                Special dictionary created by 'multiprocessing.Manager()'
                to be shared across multiple independent processes

        Returns:
            bool: True if the function runs successfully, otherwise Error
        '''
        # Encrypts the data
        encrypted_data = "".join([chr_((ord_(data[pos])+ord_(key[pos]))%max_range) for pos in range(len(data))])

        # Adds the data to the shared_dictionary
        shared_dictionary[segment] = encrypted_data

        return True

    still_alive = []


    if segments > 1:
        # Starting multiple process for the 
        # 'multiprocess_encryption' function
        for data_segment,key_segment,process in zip(child_segmented_data, child_segmented_key, range(1,segments)):
            p = Process(target=multiprocess_encryption, args=(key_segment, data_segment, process, shared_dictionary))
            p.start()
            still_alive.append(p)


    # Encrypts the first segment of data with the main process
    multiprocess_encryption(segmented_key[:1][0], segmented_data[:1][0], 0, shared_dictionary)

    # Waits until all processes have finished and terminated
    while still_alive:
        removal = [item for item in still_alive if not item.is_alive()]
        [still_alive.remove(item) for item in removal]
    
    # Encrypt the metadata
    key = sha256(metadata_key)
    encrypted_metadata = "".join([chr_((ord_(metadata[pos])+ord_(key[pos]))%130) for pos in range(len(metadata))])

    # Adds the metadata to the start of the data
    encrypted_data = "".join([shared_dictionary[count] for count in range(segments)])
    shared_dictionary = None;

    # Creating a seemingly random position to place the metadata in the data
    key = sha256(str(metadata_key))
    splitter_chars = key[2:12]

    # Turns the key to its integer equivalent and takes it by
    # the mode of the len of the data
    all_encrypted_data_length = len(encrypted_data)+len(splitter_chars)+len(encrypted_metadata)
    position = int("".join(list(map(str, map(ord, key)))))%(all_encrypted_data_length)
    if position >= all_encrypted_data_length-30:
        position = int(all_encrypted_data_length * .2)

    # Join the metadata with the regular data
    index_data = encrypted_data[position:position+100]

    encrypted_data = encrypted_data.split(index_data)
    encrypted_data = encrypted_data[0]+encrypted_metadata+splitter_chars+index_data+encrypted_data[1]

    return encrypted_data.encode()


def decrypt(key:"any data type", encrypted_data:bytes, processes=cpu_count()) -> "origional data":
    '''
    Decrypts the data by subtracting each characters integer equivalent
    by the integer equivalent of the character in the same position in 
    the new key variable generated by the 'key parameter'

    Args:
        key (any data type):
            Used to create a larger key which is used for encrypting the data
        encrypted_data (bytes):
            The encrypted bytes returned by the 'encrypt' function
        processes (int, preset:All available CPU cores):
            The amount of processes allowed to run simultaneously, 
            the more allowed, the faster the decryption.
            
            ( Multi-cored decryption only currently available on linux )

    Returns:
        The origional data
            
    '''
    # ListCrypt currently does not support multiprocessing in windows
    if platform.system() != "Linux":
        processes = 1

    # Converts the metadata to variables for easy usability
    confirmation_data = "39"
    metadata_dictionary = pull_metadata(sha256(str(key)), encrypted_data)
    origional_data_type = metadata_dictionary["type"]
    max_range = metadata_dictionary["range"]
    data = metadata_dictionary["data"]

    # Creates a new, longer key from the origional 'key' variable
    # to match or exceed the length of the data
    key = create_key(str(key), len(data))

    # Creates a dictionary that is shared across independent processes
    shared_dictionary = Manager().dict()

    # Splits the data and key into segments for even
    # distribution across cpu cores
    segments = processes
    segmented_data = segment_data(data, segments)
    segmented_key = segment_data(key, segments)

    # Leaving out the first segment for the main process to run
    # after it starts the child processes
    child_segmented_data = segmented_data[1:]
    child_segmented_key = segmented_key[1:]

    def multiprocess_decryption(key, data:str, segment:int, shared_dictionary:dict) -> bool:
        '''
        Takes chuncks of data from each process and adds them to a shared
        dictionary, with the 'segment' parameter being the origional 
        position for concatenation after encryption

        Args:
            data (str):
                The string of data to be decrypted
            segment (int):
                The origional location of the data in the list variable
                'segmented_data', so it can be concatenated back into
                the correct order from the dictionary
            shared_dictionary (dict):
                Special dictionary created by 'multiprocessing.Manager()'
                to be shared across multiple independent processes

        Returns:
            bool: True if the function runs successfully, otherwise Error
        '''
        # Decrypts the data
        decrypted_data = "".join([chr_((ord_(data[pos])-ord_(key[pos]))%max_range) for pos in range(len(data))])
        # Adds the data to the shared_dictionary
        shared_dictionary[segment] = decrypted_data

    still_alive = []

    if segments > 1:
        # Starting multiple process for the 'multiprocess_decryption' function
        for data_segment,key_segment,process in zip(child_segmented_data, child_segmented_key, range(1,segments)):
            p = Process(target=multiprocess_decryption, args=(key_segment, data_segment, process, shared_dictionary))
            p.start()
            still_alive.append(p)


    # Encrypts the first segment of data with the main process
    multiprocess_decryption(segmented_key[:1][0], segmented_data[:1][0], 0, shared_dictionary)

    # Waits until all processes have finished and terminated
    while still_alive:
        removal = [item for item in still_alive if not item.is_alive()]
        [still_alive.remove(item) for item in removal]

    # Concatenating the data from the shared dictionary, into one string
    decrypted_data = "".join([shared_dictionary[count] for count in range(segments)])

    # Pulls confirmation text from data to verify successful decryption
    pulled_confirmation = decrypted_data[:len(confirmation_data)]

    # If True the origional data is returned, 
    # otherwise the function returns False
    if pulled_confirmation == confirmation_data:
        decrypted_data = decrypted_data[len(confirmation_data):]

        # Converting data back to origional type
        return convert_data_back((decrypted_data, origional_data_type))

    else:
        return False

def remove_image_exif(path:str) -> bool:
    '''
    Removes the metadata from the provided image, which may cause
    unwanted effects like image rotating, but may reduce the file
    size greatly
    
    Args:
        path (str):
            Path to the image

    Returns:
        bool:
            True if the image's exif data is removed successfully, will return
            False if the process fails, or the image has no exif data
    '''
    try:
        from PIL import Image
        image = Image.open(path)
        data = list(image.getdata())
        image_without_exif = Image.new(image.mode, image.size)
        image_without_exif.putdata(data)
        image_without_exif.save(path)

        return True
    except Exception:
        return False


def encrypt_file(key:'any data type', path:str, metadata_removal=True) -> bool:
    '''
    This function enables the easy encryption of files

    Args:
        key (any data type):
            The key used to encrypt the file, can be any data type
            
        path (str):
            The location of your file in your filesystem

        metadata_removal (bool, *optional):
            Removes any exif data from your images, 
            which may cause side effects like image rotating
    
    Returns:
        bool:
            True if the file is encrypted successfully

    '''
    # Attempts to remove meta data from images to reduce storage size
    if metadata_removal:
        remove_image_exif(path)
    # Allows for opening both string and byte files without issue
    try:
        with open(path, "r")as file:
            encrypted_file_data = file.read()
    except:
        with open(path, "rb")as file:
            encrypted_file_data = file.read()

    encrypted_data = encrypt(key, encrypted_file_data)

    with open(path, 'wb')as f:
        f.write(encrypted_data)

    return True


def decrypt_file(key:'any data type', path:str) -> bool:
    '''
    This function enables the easy decryption of files
    
    Args:
        key (any data type):
            The key used to decrypt the file, can be any data type
            
        path (str):
            The location of your file in your filesystem
    
    Returns:
        bool:
            True if the file is decrypted successfully

    '''
    try:
        with open(path, "rb")as file:
            encrypted_data = file.read()
    except Exception:
        raise NameError('Incorrect File Path')

    decrypted_data = decrypt(key, encrypted_data)

    # Returns False if decryption process fails
    if not decrypted_data:
        return False

    # Allows for opening both string and byte files without issue
    if type(decrypted_data) == str:
        with open(path, "w")as file:
            file.write(decrypted_data)
    if type(decrypted_data) == bytes:
        with open(path, "wb")as file:
            file.write(decrypted_data)
    
    return True


if __name__=="__main__":
    #Example use of the 'encrypt_file()' and 'decrypt_file()' functions
    if True:
        file_path = "file.txt"
        key = "example key"

        #Encrypts the data from the file, back into the file
        encrypt_file(key, file_path)
    
        #Decrypts the data from the file, back into the file
        decrypt_file(key, file_path)

    #Example use of the 'encrypt()' and 'decrypt()' functions
    if False:
        data = "example data" 
        key = "example key"

        e = encrypt(key, data)

        d = decrypt(key, e)

        print(f"Encrypted Data: {e}")

        print(f"Decrypted Data: {d}")

