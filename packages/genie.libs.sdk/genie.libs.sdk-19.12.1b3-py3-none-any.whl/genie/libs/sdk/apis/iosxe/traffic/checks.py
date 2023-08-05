"""Common functions for traffic checks"""

# Python
import re
import logging

# Genie
from genie.utils.timeout import Timeout
from genie.harness.exceptions import GenieTgnError

# Commons
from genie.libs.sdk.apis.utils import analyze_rate

log = logging.getLogger(__name__)


def set_traffic_transmit_rate(
    testbed, traffic_stream, set_rate, tolerance, max_time, check_interval
):
    """Set stream transmit rate

        Args:
            testbed (`obj`): Testbed object
            traffic_stream (`str`): Traffic stream name
            set_rate (`int`): Traffic set rate
            tolerance (`int`): Traffic tolerance
            max_time (`int`): Retry maximum time
            check_interval (`int`): Interval in seconds to do recheck

        Returns:
            None
        Raises:
            KeyError: Could not find device on testbed
            Exception: Failed to set transmit rate
    """
    try:
        ixia = testbed.devices["IXIA"]
    except KeyError:
        raise KeyError("Could not find IXIA device on testbed")

    rate, rate_unit, original_rate = analyze_rate(set_rate)

    # IXIA statistics doesn't have 'Gbps' option
    if rate_unit == "Gbps":
        original_rate = original_rate * 1000
        rate_unit = "Mbps"

    # Set the transmit rate
    try:
        ixia.set_layer2_bit_rate(
            traffic_stream=traffic_stream,
            rate=original_rate,
            rate_unit=rate_unit,
            start_traffic=False,
        )
    except Exception as e:
        raise Exception("Failed to set the transmit rate due to: {}".format(e))


def check_traffic_transmitted_rate(
    testbed,
    traffic_stream,
    set_rate,
    tolerance,
    max_time,
    check_interval,
    check_stream=True,
):
    """Check transmitted rate was set correctly or not

        Args:
            testbed (`obj`): Testbed object
            traffic_stream (`str`): Traffic stream name
            set_rate (`int`): Traffic set rate
            tolerance (`int`): Traffic tolerance
            max_time (`int`): Retry maximum time
            check_interval (`int`): Interval in seconds to do recheck

        Returns:
            None
        Raises:
            KeyError: Could not find device on testbed
            Exception: Traffic drops found
    """
    try:
        ixia = testbed.devices["IXIA"]
    except KeyError:
        raise KeyError("Could not find IXIA device on testbed")

    rate, rate_unit, original_rate = analyze_rate(set_rate)

    # IXIA statistics doesn't have 'Gbps' option
    if rate_unit == "Gbps":
        original_rate = original_rate * 1000
        rate_unit = "Mbps"

    # Start the traffic stream
    ixia.start_traffic_stream(traffic_stream, check_stream)

    log.info(
        "Verify the transmitted rate was set correctly, "
        "will retry for {} every {} seconds".format(max_time, check_interval)
    )

    timeout = Timeout(max_time, check_interval)
    while timeout.iterate():

        # Print IXIA traffic streams when doing a traffic check/retrieve call
        ixia.create_traffic_streams_table()

        # Check the transmitted rate was set correctly
        transmitted_rate = ixia.get_traffic_items_statistics_data(
            traffic_stream=traffic_stream,
            traffic_data_field="Tx Rate ({})".format(rate_unit),
        )

        expected_rate, expected_rate_unit, original_rate, tolerance_margin = get_traffic_rates(
            str(original_rate), tolerance
        )

        if (
            float(transmitted_rate) < original_rate + tolerance_margin
            and float(transmitted_rate) > original_rate - tolerance_margin
        ):
            log.info(
                "Transmitted rate '{transmitted_rate}{rate_unit}' is within "
                "the set rate '{rate}{rate_unit}', tolerance is {tolerance}%".format(
                    transmitted_rate=transmitted_rate,
                    rate=original_rate,
                    rate_unit=rate_unit,
                    tolerance=tolerance,
                )
            )
            return
        else:
            timeout.sleep()

    raise Exception(
        "Retrieved transmit rate for traffic stream '{}' is '{}' while "
        "we did set '{}{}', tolerance is {}%".format(
            traffic_stream,
            transmitted_rate,
            original_rate,
            rate_unit,
            tolerance,
        )
    )


def check_traffic_expected_rate(
    testbed, traffic_stream, expected_rate, tolerance
):
    """Check the expected rate

        Args:
            testbed (`obj`): Testbed object
            traffic_stream (`str`): Traffic stream name
            expected_rate (`str`): Traffic expected received rate
            tolerance (`str`): Traffic loss tolerance percentage

        Returns:
            None
        Raises:
            KeyError: Could not find device on testbed
            Exception: Traffic drops found
    """
    try:
        ixia = testbed.devices["IXIA"]
    except KeyError:
        raise KeyError("Could not find IXIA device on testbed")

    # Print IXIA traffic streams when doing a traffic check/retrieve call
    table = ixia.get_traffic_item_statistics_table(["Rx Rate (Mbps)"])

    # needed for logic in next block
    setattr(table, 'border', False)
    setattr(table, 'header', False)

    # gets the row that 'traffic_stream' is on
    row = [x.strip() for x in table.get_string(fields=['Traffic Item']).splitlines()].index(traffic_stream)
    # gets the 'Rx Rate (Mbps)' value at the above row
    retrieved_rate = float(table.get_string(fields=['Rx Rate (Mbps)'], start=row, end=row+1))

    # Since retrieved_rate is always going to be Mbps
    retrieved_rate_in_bytes = retrieved_rate * 1000000

    if ">" in expected_rate:
        rate_in_bytes, original_rate_unit, original_rate, _ = get_traffic_rates(
            expected_rate.split(">")[1], tolerance
        )

        log.info('Rate provided in datafile is {original_rate}{original_rate_unit}. '
                 'Converted to Mbps it is {converted}Mbps'
                 .format(original_rate=original_rate,
                         original_rate_unit=original_rate_unit,
                         converted=rate_in_bytes / 1000000))

        tolerance_in_bytes = rate_in_bytes * (tolerance / 100)

        if retrieved_rate_in_bytes > (rate_in_bytes - tolerance_in_bytes):
            log.info(
                "Expected rate for traffic stream '{stream}' is "
                "'{expected} Mbps' (tolerance {tolerance}%, greater than "
                "'{expected_after_tolerance} Mbps') and got '{actual} Mbps'"
                    .format(
                    stream=traffic_stream,
                    expected=rate_in_bytes / 1000000,
                    tolerance=tolerance,
                    expected_after_tolerance=(rate_in_bytes - tolerance_in_bytes) / 1000000,
                    actual=retrieved_rate
                )
            )
        else:
            raise Exception(
                "Expected rate for traffic stream '{stream}' is "
                "'{expected} Mbps' (tolerance {tolerance}%, greater than "
                "'{expected_after_tolerance} Mbps') and got '{actual} Mbps'"
                    .format(
                    stream=traffic_stream,
                    expected=rate_in_bytes / 1000000,
                    tolerance=tolerance,
                    expected_after_tolerance=(rate_in_bytes - tolerance_in_bytes) / 1000000,
                    actual=retrieved_rate
                )
            )
    else:
        rate_in_bytes, original_rate_unit, original_rate, _ = get_traffic_rates(
            expected_rate, tolerance)

        log.info('Rate provided in datafile is {original_rate}{original_rate_unit}. '
                 'Converted to Mbps it is {converted}Mbps'
                 .format(original_rate=original_rate,
                         original_rate_unit=original_rate_unit,
                         converted=rate_in_bytes / 1000000))

        tolerance_in_bytes = rate_in_bytes * (tolerance / 100)

        if (
            retrieved_rate_in_bytes < rate_in_bytes + tolerance_in_bytes
            and retrieved_rate_in_bytes > rate_in_bytes - tolerance_in_bytes
        ):

            log.info(
                "Expected rate for traffic stream '{stream}' is '{expected} Mbps' "
                "(tolerance {tolerance}%, {gt} Mbps<>{lt} Mbps) and got '{actual} Mbps'"
                    .format(
                    stream=traffic_stream,
                    expected=rate_in_bytes / 1000000,
                    tolerance=tolerance,
                    gt=(rate_in_bytes - tolerance_in_bytes) / 1000000,
                    lt=(rate_in_bytes + tolerance_in_bytes) / 1000000,
                    actual=retrieved_rate,
                )
            )
        else:
            raise Exception(
                "Expected rate for traffic stream '{stream}' is '{expected} Mbps' "
                "(tolerance {tolerance}%, {gt} Mbps<>{lt} Mbps) and got '{actual} Mbps'"
                    .format(
                    stream=traffic_stream,
                    expected=rate_in_bytes / 1000000,
                    tolerance=tolerance,
                    gt=(rate_in_bytes - tolerance_in_bytes) / 1000000,
                    lt=(rate_in_bytes + tolerance_in_bytes) / 1000000,
                    actual=retrieved_rate,
                )
            )


def check_traffic_drop_count(testbed, traffic_stream, drop_count):
    """Check for the drop count

        Args:
            testbed (`obj`): Testbed object
            traffic_stream (`str`): Traffic stream name
            drop_count (`str`): Expected drop count

        Returns:
            None
        Raises:
            KeyError: Could not find device on testbed
            Exception: Traffic drops found
    """
    try:
        ixia = testbed.devices["IXIA"]
    except KeyError:
        raise KeyError("Could not find IXIA device on testbed")

    # Stop all traffic streams
    ixia.stop_traffic()

    try:
        # Print IXIA traffic streams when doing a traffic check/retrieve call
        ixia.get_traffic_item_statistics_table(["Frames Delta"])

        # Check for no drops
        dropped_frames = ixia.get_traffic_items_statistics_data(
            traffic_stream=traffic_stream, traffic_data_field="Frames Delta"
        )
    except GenieTgnError as e:
        raise Exception(
            "Couldn't extract the dropped IXIA frames for traffic flow {}".format(
                traffic_stream
            )
        )

    if int(dropped_frames) <= int(drop_count):
        log.info(
            "Dropped IXIA frames for traffic flow '{}' is '{}' which is less than"
            " or equal to the expected drop count '{}'".format(
                traffic_stream, dropped_frames, drop_count
            )
        )
        return
    else:
        raise Exception(
            "Dropped IXIA frames for traffic flow '{}' is '{}' which is greater than"
            " the expected drop count '{}'".format(
                traffic_stream, dropped_frames, drop_count
            )
        )


def get_traffic_rates(expected_rate, tolerance):
    """Retrieve the formated traffic rates and tolerance margin

        Args:
            expected_rate (`str`): Expected traffic rate
            tolerance (`str`): Tolerance margin

        Returns:
            expected_rate, expected_rate_unit, original_rate, tolerance_margin
        Raise:
            Exception: Failed analyzing rate
    """
    try:
        expected_rate, expected_rate_unit, original_rate = analyze_rate(
            expected_rate
        )
    except Exception as e:
        raise Exception("{}".format(e))

    # Calculate tolerance
    tolerance_margin = float(original_rate) * (tolerance / 100)

    return expected_rate, expected_rate_unit, original_rate, tolerance_margin
