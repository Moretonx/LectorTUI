from mfrc522 import MFRC522
import time

key_A0A5 = [0xA0, 0xA1, 0xA2, 0xA3, 0xA4, 0xA5]
key_FF   = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]

reader = MFRC522()

print("Acerca la tarjeta...")

try:
    while True:
        (status, _) = reader.MFRC522_Request(reader.PICC_REQIDL)
        (status, uid) = reader.MFRC522_Anticoll()

        if status == reader.MI_OK:
            print("UID:", uid)

            reader.MFRC522_SelectTag(uid)

            block = 68  # tu bloque del RUT

            for key in (key_A0A5, key_FF):
                st = reader.MFRC522_Auth(reader.PICC_AUTHENT1A, block, key, uid)
                print("AUTH status con key", key, "=>", st)

                if st == reader.MI_OK:
                    rut = reader.MFRC522_Read(68)
                    nombre = reader.MFRC522_Read(72)
                    paterno = reader.MFRC522_Read(73)
                    materno = reader.MFRC522_Read(74)

                    print("RUT:", rut)
                    print("NOMBRE:", nombre)
                    print("PATERNO:", paterno)
                    print("MATERNO:", materno)

                    reader.MFRC522_StopCrypto1()
                    raise SystemExit

                reader.MFRC522_StopCrypto1()

        time.sleep(0.2)

finally:
    reader.Close_MFRC522()
