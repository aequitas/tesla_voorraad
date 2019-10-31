from prometheus_client import start_http_server, Gauge, REGISTRY
from collections import defaultdict
import urllib.parse
import requests
import json
import time
import random
import datetime
import logging

URL = "https://www.tesla.com/api.php"
MODELS = ["m3", "s", "mx"]
ATTRIBUTES = ["Model", "PAINT", "TRIM", "INTERIOR", "WHEELS", "AUTOPILOT"]

PORT = 8000
INTERVAL = datetime.timedelta(minutes=5)


def get_teslas(model="m3"):
    query = {
        "query": {
            "model": model,
            "condition": "new",
            "options": {},
            "arrangeby": "Price",
            "order": "asc",
            "market": "NL",
            "language": "nl",
            "super_region": "europe",
            "lng": "",
            "lat": "",
            "zip": "",
            "range": 0,
        },
        "offset": 0,
        "count": 50,
        "outsideOffset": 0,
        "outsideSearch": False,
    }

    params = {
        "m": "tesla_cpo_marketing_tool",
        "a": "inventory_search",
        "query": json.dumps(query),
    }

    headers = {
        "authority": "www.tesla.com",
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.70 Safari/537.36",
        "referer": "https://www.tesla.com/nl_NL/inventory/new/m3?arrangeby=plh&zip=6661&range=0",
    }

    response = requests.get(URL, params=params, headers=headers)
    response.raise_for_status()

    return [t for t in response.json()["results"] if isinstance(t, dict)]


# ADL_OPTS: ["FREE_SUPERCHARGING"]
# AUTOPILOT: ["AUTOPILOT_TWO"]
# AdjustedSalesDiscountPercentage: ""
# BATTERY: ""
# CABIN_CONFIG: ""
# CPORefurbishmentStatus: null
# CalculateLease: ""
# ChildMapping: ""
# ComboID: ""
# CompositorViews: {frontView: "STUD_3QTR_V2", interiorView: "STUD_SEAT_V2", sideView: "STUD_SIDE_V2"}
# CountryCode: "NL"
# CurrencyCode: "EUR"
# DECOR: ["FIGURED_ASH"]
# DRIVE: ["DV2W"]
# DeliveryDateDisplay: false
# DestinationHandlingFee: 980
# DisplayWarranty: true
# ExternalListingId: ""
# HEADLINER: ["DARK_HEADLINER"]
# HasMarketingOptions: true
# INTERIOR: ["BLACK"]
# IsDemoVehicle: false
# IsLegacy: false
# Language: "nl"
# LeaseAvailabilityDate: ""
# ListForSale: true
# ListingType: "public"
# Model: "ms"
# NearByDeliveryRegion: ""
# NotForSale: false
# Odometer: 11
# OdometerType: "Km"
# OptionCodeList: "$MDLS,$PPSB,$RFFR,$WTTC,$INFBP,$PI01,$APBS,$SC05,$CPF1,$MTS01"
# OptionCodeListWithPrice: ""
# OptionCodeSpecs: {C_DESIGN: {code: "C_DESIGN", name: "Design", options: []},…}
# OriginalInCustomerGarageDate: ""
# PAINT: ["BLUE"]
# PreownedWarrantyEligibility: null
# Price: 80218
# ROOF: ["ROOF_GLASS"]
# RecyclingFee: ""
# TRIM: ["SRAWD"]
# TitleStatus: "NEW"
# TransportationFee: 0
# TrimCode: "$MTS01"
# TrimName: "Model S Standard Range"
# VIN: "5YJSA7E22KF342336"
# Variant: "ms"
# VehicleBadge: ""
# VehiclePhotos: ""
# VehicleRegion: ""
# WHEELS: ["TWENTY_ONE"]
# WarrantyBatteryMile: null
# WarrantyBatteryYear: 8
# WarrantyMile: 80000
# WarrantyYear: 4
# Year: 2019
# token: "$2y$10$Qjy7eihtQ1dP5r8F1to05ePoHrj45goR5m12G.fx5M45dzhmPDz9e"

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    teslas_in_stock = Gauge(
        "tesla_voorraad_nl",
        "Tesla Voorraad in Nederland",
        [a.lower() for a in ATTRIBUTES],
    )

    start_http_server(PORT)

    logging.info(f"listening on: http://127.0.0.1:{PORT}")

    while True:
        teslas_in_stock._metrics.clear()
        for model in MODELS:
            for tesla in get_teslas(model=model):

                def convert(value):
                    if isinstance(value, list):
                        return "/".join(value)
                    return value

                attrs = {a.lower(): convert(tesla[a]) for a in ATTRIBUTES}
                teslas_in_stock.labels(**attrs).inc()
        time.sleep(INTERVAL.seconds)
