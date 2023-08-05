# BLECryptracer  #
These scripts require Python v3+ and have been tested with Androguard v3.3.5. These (and all dependencies) should be installed on your system.

In order to install dependencies you can 

```
pip install -r requirements.txt
```

In order to analyse an APK you will need to type the following
```
python BLECryptracer.py -i APK_FILE_TO_ANALYSE [-o OUTPUT_FILE_IN_JSON]
```

If no output file is provided, the result will be saved in a file named output.json. 

During execution several files and folders may be created. Those will be deleted after exectuion.



The output JSON file contains the following: 
```
FILENAME - The name of the APK file
PACKAGE - The package name (e.g., com.test.app)
XETVALUE_CALL - True if the APK makes calls to one of the android.BluetoothGattCharacteristic setValue or getValue methods. The scripts stop processing an APK if this is False.
CRYPTO_USE - True if the APK contains *any* calls to the javax.crypto or java.security methods. The scripts stop processing an APK if this is False. 
CRYPTO_IN_XETVALUE - True if cryptographically-processed BLE data was identified. False otherwise
CONFIDENCE_LEVEL_XETVALUE - One of High, Medium or Low, depending on how certain we are of the result. Only relevant when CRYPTO_IN_XETVALUE is True
NET_USE - True if the APK contains any calls to java.net.URLConnection, java.net.HttpURLConnection or javax.net.ssl.HttpsURLConnection. Only present in the output of the setvalue script.
LOCATION_XETVALUE - The last processed method (that calls setValue or getValue) 
LOCATION_CRYPTO_XETVALUE - The method that calls the crypto-library (linked to the BLE data)
NUM_XETVALUE_METHODS - The total number of calls to setValue/getValue. Note that the scripts stop processing at the first instance where crypto is identified.
ALL_XETVALUE_METHODS - A list of all methods that call setValue/getValue
TIME_TAKEN_XETVALUE - The time taken to process an APK
BLE_UUIDS - UUIDs that have been extracted with BLE functionality. These can be of several kinds depending on how they were extracted.
CLASSIC_UUIDS - UUIDs that belong to Classic Bluetooth. These are not relevant at the moment.
```