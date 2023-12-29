from pathlib import Path
import os
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher, Router, html
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, BotCommand, FSInputFile,
)

from file_utils import Utils
from task_queue import TaskQueue

TOKEN = "488786370:AAH4HBXr6umNHE25H0rdXdbVpItc071LYr8"

# semaphore = asyncio.Semaphore(5)

# All handlers should be attached to the Router (or Dispatcher)
router = Router()
task_queue = TaskQueue()
utils = Utils()
data_dir = utils.path_from_root('data/messages')
uploads_dir = utils.path_from_root('data/uploads')
results_dir = utils.path_from_root('data/results')


def load_message_texts():
    command_texts = {}
    for file in os.listdir(data_dir):
        if file.endswith('.txt'):
            command_texts[file.split('.')[0]] = "\n".join(utils.load_list_from_file(os.path.join(data_dir, file)))
    return command_texts


command_texts = load_message_texts()

router = Router()
bot = Bot(token=TOKEN, parse_mode="HTML")


class Form(StatesGroup):
    process = State()
    awaiting_task = State()
    language = State()


def format_status_message(task_id):
    task = task_queue.get_task(task_id)
    message = f"Task id: {task.task_id}\n"
    message += f"Status: {task.status}"
    if task.status == 'error':
        message += f"\nError message: {task.error_message}"
    return message


@router.message(Command("start"))
async def command_start(message: Message, state: FSMContext) -> None:
    text = command_texts['start']
    await message.answer(
        text,
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(lambda c: c.document)
async def upload_file(message: Message, state: FSMContext) -> None:
    supported_file_types = ['.xlsx', '.xls', '.csv']
    if not message.document:
        return

    file_id = message.document.file_id
    file = await bot.get_file(file_id)
    file_path = file.file_path
    base_name = os.path.basename(file_path)
    extension = os.path.splitext(base_name)[1].lower()
    if extension not in supported_file_types:
        await message.answer(f'Only the following file formats are supported: {", ".join(supported_file_types)}')
        return
    if extension == ".csv":
        if file.file_size > 1000000:
            await message.answer('File size should be less than 1 Mb')
            return
    else:
        if file.file_size > 100000:
            await message.answer('File size should be less than 100 kb')
            return

    target_dir = os.path.join(uploads_dir, str(message.chat.id))
    Path(target_dir).mkdir(parents=True, exist_ok=True)
    destination = os.path.join(target_dir, base_name)
    await bot.download_file(file_path, destination)

    data = await state.get_data()
    data['filename'] = destination
    await state.set_data(data)
    if 'task' not in data:
        menu_main = [[InlineKeyboardButton(text='Specify task', callback_data='formulate_task')]]
        reply_markup = InlineKeyboardMarkup(inline_keyboard=menu_main)
        await message.answer("The table was successfully uploaded!", reply_markup=reply_markup)
    else:
        await queue_task(message, state)


@router.message(Command("process"))
async def command_process(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.process)
    text = command_texts['process']
    menu_main = [
        [InlineKeyboardButton(text='Upload table', callback_data='upload_table')],
        [InlineKeyboardButton(text='Specify task', callback_data='formulate_task')],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=menu_main)

    await message.answer(text, reply_markup=reply_markup)


@router.callback_query(lambda c: c.data)
async def process_callback_buttons(query: CallbackQuery, state: FSMContext):
    code = query.data
    chat_id = query.message.chat.id
    if code.startswith("check_status"):
        task_id = code.split('/')[1]
        message_text = format_status_message(task_id)
    else:
        message_text = command_texts[code]

    if code == 'formulate_task':
        await state.set_state(Form.awaiting_task)
    data = await state.get_data()
    if "message_ids" not in data:
        data["message_ids"] = []
    data["message_ids"].append(query.message.message_id)
    await state.set_data(data)
    await bot.send_message(chat_id, message_text)


@router.message(Form.awaiting_task)
async def receive_task(message: Message, state: FSMContext) -> None:
    if message.text.casefold() == "/cancel":
        data = await state.get_data()
        await state.clear()
        await clear_markup(message, data)
        await message.answer("Cancelled")
        return

    if len(message.text) < 20:
        await message.answer("Task should be at least 20 characters long")
        return

    current_state = await state.get_state()
    if current_state is None:
        return

    data = await state.get_data()
    data["task"] = message.text
    await state.set_data(data)
    if not data.get('filename'):
        await message.answer("Your task is accepted. Please upload table")
        return

    await queue_task(message, state)


async def queue_task(message, state: FSMContext) -> None:
    data = await state.get_data()
    await clear_markup(message, data)
    task_id = task_queue.add_task(message.chat.id, data['task'], data['filename'])
    await state.clear()
    menu_main = [
        [InlineKeyboardButton(text='Check status', callback_data='check_status/' + str(task_id))],
    ]
    reply_markup = InlineKeyboardMarkup(inline_keyboard=menu_main)

    await message.answer(
        f"Your task is in the queue. You will be notified when it is complete. \nTask id: {task_id}",
        # reply_markup=ReplyKeyboardRemove(),
        reply_markup=reply_markup,
    )


async def clear_markup(message, data: dict) -> None:
    if "message_ids" not in data:
        return
    message_ids = data["message_ids"]
    if message_ids:
        for message_id in message_ids:
            try:
                await bot.edit_message_reply_markup(message.chat.id, message_id)
            except:
                pass


@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    data = await state.get_data()
    await clear_markup(message, data)

    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Cancelled.",
        reply_markup=ReplyKeyboardRemove(),
    )


async def notify_user(task):
    chat_id, task_id = task.chat_id, task.task_id
    await bot.send_message(chat_id, f"Task {task_id} is complete")
    result_filename = os.path.join(results_dir, task.result_filename)
    basename = os.path.basename(result_filename)
    file_link = FSInputFile(result_filename, filename=basename)
    await bot.send_document(chat_id, file_link)


async def listen_queue():
    tasks = task_queue.get_completed_unnotified_tasks()
    for task in tasks:
        if task.notification_sent == 1:
            continue
        await notify_user(task)
        task_queue.mark_as_notified(task)


async def queue_listener():
    while True:
        await asyncio.sleep(1)
        # print("Listening queue")
        await listen_queue()


async def main():
    dp = Dispatcher()
    dp.include_router(router)
    commands = [
        BotCommand(command="/start", description="Start conversation"),
        BotCommand(command="/process", description="Process table"),
        BotCommand(command="/cancel", description="Cancel current action"),
    ]
    await bot.set_my_commands(commands)

    loop = asyncio.get_event_loop()
    loop.create_task(queue_listener())

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())