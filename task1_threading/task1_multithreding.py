import threading
from pathlib import Path
import time
from colorama import Fore, Style, init
init(autoreset=True)


# Отримати всі текстові файли в каталозі
def avaliable_files(directory_path):
    return list(Path(directory_path).glob("*.txt"))


# Що за текст у файлі
def display_content(file_path):
    with open(file_path, "r", encoding="utf-8", errors="ignore") as file:
        print(f"{Fore.GREEN}Вміст файлу '{file_path}':\n{Style.RESET_ALL}")
        print(file.read())


# Шукаємо ключові слова
def search_keywords(files_subset, keywords, result_list, result_lock):
    keywords_normal = [keyword.lower() for keyword in keywords]
    results_local = []

    for file in files_subset:
        try:
            with file.open("r", encoding="utf-8", errors="ignore") as file:
                content = file.read().lower()  # все робимо однаковим у нижньому регістрі
                for keyword, original_keyword in zip(keywords_normal, keywords):
                    count = content.count(keyword)
                    if count > 0:
                        # файл, слово , рахунок
                        results_local.append(
                            (file.name, original_keyword, count))
        except Exception as e:
            print(f"{Fore.RED}Помилка читання {file.name}: {e}{Style.RESET_ALL}")
            continue

    with result_lock:  # контроль даних
        result_list.extend(results_local)


# розбити файли для розподілу по потоках
def chanky(data_list, number_of_chunks):
    chunk_size = len(data_list) // number_of_chunks
    return [data_list[i * chunk_size:(i + 1) * chunk_size] for i in range(number_of_chunks - 1)] + [data_list[(number_of_chunks - 1) * chunk_size:]]


# ---------------Робота програми і інтерфейс-------------------------------------
def main():
    start_time = time.time()

    FILES_DIR = Path(__file__).parent / "../files"
    available_files = avaliable_files(FILES_DIR)
    print(f"Шукаємо в каталозі: {FILES_DIR.resolve()}")

    if not available_files:
        print(f"{Fore.RED}Файли не знайдено.{Style.RESET_ALL}")
        return

    print(f"{Fore.BLUE}Доступні файли:{Style.RESET_ALL}")
    for idx, file in enumerate(available_files, 1):
        print(f"{idx}. {file.name}")

    selected_file = None
    while True:
        selected = input(
            f"{Fore.LIGHTGREEN_EX}Введіть номер файлу для перегляду, якщо написати 'exit' -> виход:{Style.RESET_ALL} ").strip()
        if selected.lower() == "exit":
            print(f"{Fore.LIGHTYELLOW_EX}Вихід із програми.{Style.RESET_ALL}")
            return
        if selected.isdigit():
            index = int(selected) - 1
            if 0 <= index < len(available_files):
                selected_file = available_files[index]
                display_content(selected_file)
                break
            else:
                print(f"{Fore.RED}Номера не існує.{Style.RESET_ALL}")
        else:
            print(f"{Fore.LIGHTCYAN_EX}Введіть число чи 'exit'.{Style.RESET_ALL}")

    keywords_input = input(
        f"{Fore.LIGHTRED_EX}Введіть слова для пошуку через кому:{Style.RESET_ALL}").strip()
    if keywords_input.lower() == "exit":
        print(f"{Fore.GREEN}Дякую, До побачення!.{Style.RESET_ALL}")
        return

    keywords = [word.strip()
                for word in keywords_input.split(",") if word.strip()]
    if not keywords:
        print(
            f"{Fore.LIGHTRED_EX}Будь ласка вводьте слова для роботи програми{Style.RESET_ALL}")
        return

    scope_input = input(
        f"{Fore.LIGHTBLUE_EX}Шукати в одному файлі написати 'один', по всіх файлах - 'всі' :{Style.RESET_ALL} ").strip().lower()

    if scope_input == "один":
        target_files = [selected_file]
    else:
        target_files = available_files

    # Шукаємо з потоками
    results = []
    results_lock = threading.Lock()
    NUM_THREADS = min(4, len(target_files))
    chunks = chanky(target_files, NUM_THREADS)
    threads = []

    for chunk in chunks:
        t = threading.Thread(target=search_keywords, args=(
            chunk, keywords, results, results_lock))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    keyword_files = {}
    for file_name, keyword, count in results:
        keyword_files.setdefault(keyword, []).append(file_name)

    end_time = time.time()
    print(f"{Fore.YELLOW}Час виконання: {end_time - start_time:.2f} сек.{Style.RESET_ALL}")

    print(f"{Fore.MAGENTA}Результати пошуку:{Style.RESET_ALL}")
    if results:
        for file_name, keyword, count in results:
            print(f"{Fore.CYAN}{file_name} --> знайдено слово{Fore.LIGHTGREEN_EX}'{keyword}' -{Fore.CYAN} {count} раз(ів){Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}У файлах слів знайдено не було.{Style.RESET_ALL}")

    print(f"\n{Fore.LIGHTYELLOW_EX}Словник результатів:{Style.RESET_ALL}")
    for keyword, file_list in keyword_files.items():
        print(f"{Fore.LIGHTCYAN_EX}'{keyword}':{Style.RESET_ALL} {file_list}")


if __name__ == "__main__":
    main()
