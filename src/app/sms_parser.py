import os, datetime as dt, pandas as pd
from config import _log
from config import DATA_PATH, PARAMS, TMP
from sms import SMS, Conversation, Thread, Session
from tqdm import tqdm

log = _log.getLogger(__name__)


def parse_sms_xml(
    xml_file: str | os.PathLike,
) -> dict[str, list[dict[str, str]]] | None:
    try:
        import xml.etree.ElementTree as ET
    except ImportError:
        log.exception("xml.etree.ElementTree not found. Are you sure its installed?")
        return
    try:
        tree = ET.parse(xml_file)
        root = tree.getroot()
    except Exception as e:
        log.exception(f"Failed to parse xml file. Exception: {str(e)}")
        return
    conversations = {}
    try:
        log.debug(f"Parsing xml file: {xml_file}")
        for i, sms in enumerate(root.iter("sms")):
            print(f"Parsing sms {i}", end="\r", flush=True)
            date = sms.get("readable_date")
            timestamp = sms.get("date")
            contact = sms.get("contact_name")
            message = sms.get("body")
            type = sms.get("type")
            conversation_id = contact

            if contact == "(Unknown)":
                continue
            if int(type) == 2:
                sender = "User"
            else:
                sender = contact
            if conversation_id not in conversations:
                conversations[conversation_id] = []
            parsed = {
                "Date": date,
                "TimeStamp": timestamp,
                "Sender": sender,
                "Message": message.strip(),
            }
            conversations[conversation_id].append(parsed)
        log.debug(f"Finished parsing xml file: {xml_file}")
    except Exception as e:
        log.exception(f"Failed to parse xml file. Exception: {str(e)}")
        return
    return conversations


def filter_conversations(
    conversations: dict[str, list[dict[str, str]]]
) -> dict[str, list[dict[str, str]]]:
    starting = len(conversations)
    log.info(f"Filtering conversations by length.\nStarting length: {starting}")
    output = {}
    delete_keys = []
    for conversation_id, messages in conversations.items():
        log.debug(f"Filtering conversation: {conversation_id}")
        if len(messages) < int(PARAMS["SMS_LEN_FILTER"]):
            delete_keys.append(conversation_id)
    for key in delete_keys:
        del conversations[f"{key}"]
    log.debug(
        f"Finished filtering conversations. deleted: {len(delete_keys)}, remaining: {len(conversations)}\nDeleted keys: {delete_keys}"
    )
    if len(conversations) == 0:
        log.exception("No conversations found after filtering")
        return
    output = conversations
    return output


def convert_to_dataframe(messages: dict[str, list[dict[str, str]]]):
    log.info("Converting messages to DataFrame")
    data = []
    log.debug(f"messages: {type(messages)} len: {len(messages)}")
    try:
        for conversation_id, messages in messages.items():
            log.debug(f"Converting messages for conversation: {conversation_id}")
            for message in messages:
                msg = {
                    "Date": message["Date"],
                    "TimeStamp": message["TimeStamp"],
                    "Sender": message["Sender"],
                    "Message": message["Message"].replace("\n", " "),
                    "Conversation_id": conversation_id,
                }
                data.append(msg)
            df = pd.DataFrame(data)
            log.debug(f"tmp csv: {os.path.join(TMP, conversation_id + '.csv')}")
            yield save_conversation_csv(df, f"{conversation_id}.csv")
            data = []
    except Exception as e:
        log.exception(f"Failed to convert messages to DataFrame. Exception: {str(e)}")
        return


def save_conversation_csv(df: pd.DataFrame, filename: str) -> os.PathLike | None:
    log.info(f"Saving conversation to CSV file: {filename}")
    try:
        filepath = os.path.join(TMP, filename)
        df.to_csv(filepath, index=False)
        return filepath, filename.split(".")[0]
    except Exception as e:
        log.exception(f"Failed to save conversation to CSV file. Exception: {str(e)}")
        return


def parse_csv_and_create_thread(csv_file_path: os.PathLike, thread_name: str, session: Session) -> Thread:  # type: ignore
    last_date = None
    output = ""
    sms_arr = []
    conversation_arr = []
    with session as session:
        try:
            thread = Thread(thread_name)
            df = pd.read_csv(csv_file_path)
            for index, row in tqdm(df.iterrows(), desc="Parsing CSV", unit="sms"):
                sms = SMS(
                    sender=row["Sender"],
                    message=row["Message"],
                    timestamp=dt.datetime.fromtimestamp(
                        float(row["TimeStamp"]) / 1000.0
                    ),
                    date=row["Date"],
                    thread_id=thread.id,
                    thread=thread,
                )
                sms_arr.append(sms)

            session.add_all(sms_arr)

            # sort sms by timestamp so that the fist sms is the first in the conversation
            sms_arr.sort(key=lambda x: x.timestamp)

            for sms in sms_arr:
                if last_date is None:
                    last_date = sms.timestamp
                date = sms.timestamp
                if date - last_date > dt.timedelta(hours=5) and output != "":
                    output += f"\n{sms.sender}: {sms.message}"
                    conversation = Conversation(
                        content=output,
                        thread_id=thread.id,
                        thread=thread,
                        date=last_date,
                    )
                    conversation_arr.append(conversation)
                    output = ""
                    last_date = date
                elif output == "":
                    output += f"[{date.strftime('%b %d, %Y %I:%M:%S %p')}]\n{sms.sender}: {sms.message}"
                    last_date = date
                else:
                    msg = str(sms.message).replace("\n", " ")
                    output += f"\n{sms.sender}: {msg}"
                    last_date = date

            if output != "":
                conversation = Conversation(
                    content=output, thread_id=thread.id, thread=thread, date=last_date
                )
                conversation_arr.append(conversation)

            session.add_all(conversation_arr)
            session.commit()

        except Exception as e:
            log.exception(
                "Failed to parse CSV and create thread. Exception: %s", str(e)
            )
            raise

    return thread


def create_all_classes(
    dir: str,
    parse: bool = False,
    from_xml: bool = False,
) -> bool:
    dir_path = os.path.join(DATA_PATH, dir)
    log.info("create_all_classes: Parsing files in %s", dir_path)
    try:
        with Session() as session:
            if parse and not from_xml:
                log.debug("create_all_classes: Parsing CSV files")
                if not os.path.exists(dir_path) or not os.path.isdir(dir_path):
                    log.exception(
                        f"create_all_classes: Invalid directory path.\nPath: {dir_path}"
                    )
                    return False
                for sms_csv in os.listdir(dir_path):
                    log.debug("create_all_classes: Parsing file %s", sms_csv)
                    cls_name = sms_csv.split(".")[0]
                    if sms_csv.endswith(".csv"):
                        csv_file_path = os.path.join(dir_path, sms_csv)
                        thread = parse_csv_and_create_thread(
                            csv_file_path, session, cls_name
                        )
                        session.add(thread)
                session.commit()
                log.info("create_all_classes: Finished parsing CSV files")
            elif from_xml:
                log.info("create_all_classes: Parsing XML file")
                xml_file = dir_path
                conversations = parse_sms_xml(xml_file)
                log.debug(f"conversations: {type(conversations)}")
                conversations = filter_conversations(conversations)
                log.debug(
                    f"conversations: {type(conversations)}, keys: {conversations.keys()}"
                )
                if conversations is None:
                    log.exception(
                        "create_all_classes: No conversations found after filtering"
                    )
                    return False
                for csv, thread_name in convert_to_dataframe(conversations):
                    thread = parse_csv_and_create_thread(csv, thread_name, session)
                    log.debug(f"thread name: {thread_name}")
                    session.add(thread)
                session.commit()
                log.info("create_all_classes: Finished parsing XML file")
            else:
                log.exception(
                    "create_all_classes: Invalid arguments. Either parse or from_xml must be True"
                )
                return False
    except Exception as e:
        log.exception(
            "create_all_classes: Failed to create classes. Exception: %s", str(e)
        )
        return False
    finally:
        session.close()
        log.info("create_all_classes: Finished creating classes")
    return True
