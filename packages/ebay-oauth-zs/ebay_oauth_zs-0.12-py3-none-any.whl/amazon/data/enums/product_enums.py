class Condition:

    USED_LIKE_NEW = 1
    USED_VERY_GOOD = 2
    USED_GOOD = 3
    USED_ACCEPTABLE = 4
    COLLECTIBLE_LIKE_NEW = 5
    COLLECTIBLE_VERY_GOOD = 6
    COLLECTIBLE_GOOD = 7
    COLLECTIBLE_ACCEPTABLE = 8
    NOT_USED = 9
    REFURBISHED = 10
    NEW = 11

    ConditionEnum = (
        (NEW, "Новое"),
        (NOT_USED, "Не использовано"),
        (USED_LIKE_NEW, "Использовано, как новое"),
        (USED_VERY_GOOD, "Использовано, очень хорошее состояние"),
        (USED_GOOD, "Использовано, хорошее состояние"),
        (USED_ACCEPTABLE, "Использовано, приемлимое состояние"),
        (REFURBISHED, "Восстановленное"),
        (COLLECTIBLE_LIKE_NEW, "Коллекционное, как новое"),
        (COLLECTIBLE_VERY_GOOD, "Коллекционное, очень хорошее состояние"),
        (COLLECTIBLE_GOOD, "Коллекционное, хорошее состояние"),
        (COLLECTIBLE_ACCEPTABLE, "Коллекционное, приемлимое состояние"),
    )


ProductTaxCodeEnum = (("A_GEN_NOTAX", "A_GEN_NOTAX"),)

FulfillmentCenterEnum = (
    ("AMAZON_NA", "Фулфилмент AMAZON"),
    ("DEFAULT", "Фулфилмент продавца"),
)

WILL_SHIP_INTERNATIONALLY_CHOICES = (
    ("1", "Только внутри страны площадки"),
    ("2", "Международная доставка"),
)

ExpeditedShippingEnum = (
    ("Domestic", "Domestic"),
    ("Domestic, International", "Domestic, International"),
    ("Domestic, Next", "Domestic, Next"),
    ("Domestic, Next, International", "Domestic, Next, International"),
    ("Domestic, Second", "Domestic, Second"),
    ("Domestic, Second, International", "Domestic, Second, International"),
    ("Domestic, Second, Next, International", "Domestic, Second, Next, International"),
    ("International", "International"),
    ("Next", "Next"),
    ("Next, International", "Next, International"),
    ("Second", "Second"),
    ("Second, International", "Second, International"),
    ("Second, Next", "Second, Next"),
    ("Second, Next, International", "Second, Next, International"),
)


BatteryCellCompositionEnum = (
    ("Alkaline", "Щёлочь"),
    ("Lithium", "Литий"),
    ("Lithium-Ion", "Литий-ион"),
    ("Lithium-Metal", "Литий-металл"),
    ("Nickel-Cadmium", "Никель-кадмий"),
    ("Nickel-Metal Hydride", "Никель-металлогидрид"),
)


BatteryTypeEnum = (
    ("battery_type_lithium_ion", "Литий-ион"),
    ("battery_type_lithium_metal", "Литий-метал"),
    ("battery_type_12v", "12V"),
    ("battery_type_9v", "9V"),
    ("battery_type_a", "A"),
    ("battery_type_aa", "AA"),
    ("battery_type_aaa", "AAA"),
    ("battery_type_aaaa", "AAAA"),
    ("battery_type_c", "C"),
    ("battery_type_cr123a", "CR123A"),
    ("battery_type_cr2", "CR2"),
    ("battery_type_cr5", "CR5"),
    ("battery_type_d", "D"),
    ("battery_type_p76", "P76"),
    ("battery_type_product_specific", "Специфично"),
)


BatteryEnergyContentEnum = (("watt_hours", "Ватт-час"),)


LithiumBatteryPackagingEnum = (
    ("batteries_only", "Только батареи"),
    ("batteries_contained_in_equipment", "Батареи внутри прибора"),
    ("batteries_packed_with_equipment", "Батареи вместе с прибором"),
)


WeightEnum = (
    ("GR", "Грамм"),
    ("KG", "Килограмм"),
    ("LB", "Фунт"),
    ("OZ", "Унция"),
)
