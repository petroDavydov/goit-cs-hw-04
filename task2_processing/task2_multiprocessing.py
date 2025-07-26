from multiprocessing import Process, Queue
from pathlib import Path
from colorama import Fore, Style, init
import time
init(autoreset=True)


# Отримати всі текстові файли в каталозі
def avaliable_files(directory_path):
    return list(Path(directory_path).glob("*.txt"))


# Що за текст у файлі
def display_content(file_path):
    try:
        with file_path.open("r", encoding="utf-8", errors="ignore") as file:
            print(f"{Fore.GREEN}Вміст файлу '{file_path.name}':\n{Style.RESET_ALL}")
            print(file.read())
    except Exception as e:
        print(
            f"{Fore.RED}Помилка при читанні файлу {file_path.name}: {e}{Style.RESET_ALL}")


# Шукаємо ключові слова
def search_keywords(files_subset, keywords, queue):
    keywords_normal = [keyword.lower() for keyword in keywords]
    results_local = []

    for file in files_subset:
        try:
            with file.open("r", encoding="utf-8", errors="ignore") as f:
                content = f.read().lower()
                for keyword, original_keyword in zip(keywords_normal, keywords):
                    count = content.count(keyword)
                    if count > 0:
                        results_local.append(
                            (file.name, original_keyword, count))
        except Exception as e:
            print(f"{Fore.RED}Помилка читання {file.name}: {e}{Style.RESET_ALL}")
            continue

    queue.put(results_local)


# розбити файли для розподілу по потоках
def chanky(data_list, number_of_chunks):
    chunk_size = len(data_list) // number_of_chunks
    return [data_list[i * chunk_size:(i + 1) * chunk_size] for i in range(number_of_chunks - 1)] + [data_list[(number_of_chunks - 1) * chunk_size:]]


# ---------------Робота програми і інтерфейс-------------------------------------
def main():
    start_time = time.time()

    FILES_DIR = Path(__file__).parent / "../files"
    available_files = avaliable_files(FILES_DIR)
    # Для розуміння чи попадаємо ми туди куди складаємо файли
    print(f"Шукаємо в каталозі: {FILES_DIR.resolve()}")

    if not available_files:
        print(f"{Fore.RED}Файли не знайдено.{Style.RESET_ALL}")
        return

    print(f"{Fore.BLUE}Доступні файли:{Style.RESET_ALL}")
    for idx, file in enumerate(available_files, 1):
        print(f"{Fore.GREEN}{idx}. {file.name}{Style.RESET_ALL}")

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
        f"{Fore.LIGHTBLUE_EX}Шукати в одному файлі написати 'один', по всіх файлах - 'всі':{Style.RESET_ALL} ").strip().lower()

    target_files = [
        selected_file] if scope_input == "один" and selected_file else available_files

    # Шукаємо з процесами
    results = []
    queue = Queue()
    NUM_PROCESSES = min(4, len(target_files))
    chunks = chanky(target_files, NUM_PROCESSES)
    processes = []

    for chunk in chunks:
        p = Process(target=search_keywords, args=(chunk, keywords, queue))
        processes.append(p)
        p.start()

    for _ in processes:
        results.extend(queue.get())

    for p in processes:
        p.join()

    keyword_files = {}
    for file_name, keyword, count in results:
        keyword_files.setdefault(keyword, []).append(file_name)

    end_time = time.time()
    print(f"{Fore.YELLOW}Час виконання: {end_time - start_time:.2f} сек.{Style.RESET_ALL}")

    print(f"{Fore.MAGENTA}Результати пошуку:{Style.RESET_ALL}")
    if results:
        for file_name, keyword, count in results:
            print(f"{Fore.CYAN}{file_name} --> знайдено слово {Fore.LIGHTGREEN_EX}'{keyword}'{Fore.CYAN} - {count} раз(ів){Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}Слів знайдено не було.{Style.RESET_ALL}")

    print(f"\n{Fore.LIGHTYELLOW_EX}Словник результатів:{Style.RESET_ALL}")
    for keyword, file_list in keyword_files.items():
        print(f"{Fore.LIGHTCYAN_EX}'{keyword}':{Style.RESET_ALL} {file_list}")


if __name__ == "__main__":
    main()
