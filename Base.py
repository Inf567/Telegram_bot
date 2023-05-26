"""
Режим открытия файла:
r - read - чтение
w - write - запись (предыдущее содержимое файла удаляется)
a - append - ДОзапись
"""
filename = r'C:\Users\Alex\Downloads\Telegram Desktop\text.txt'


def write_to_db(user_id, grade, name, photo):
    user_id = str(user_id)
    with open(filename, 'a',encoding='utf-8') as file:
        file.write(user_id)
        file.write('\t',)
        file.write(grade)
        file.write('\t')
        file.write(name)
        file.write('\t')
        file.write(photo)
        file.write('\n')


def delete_user_from_db(my_user_id):
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    with open(filename, 'w', encoding='utf-8') as file:
        for line in lines:
            if len(line.strip().split("\t"))==4:
                user_id, grade, name, photo = line.strip().split('\t')
                if str(my_user_id) != user_id:
                    file.write(line)


def update_class_in_db(user_id, new_grade):
    user_id = str(user_id)
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    updete_lines = []
    for line in lines:
        if len(line.strip().split("\t")) == 4:
            current_user_id, grade, name, photo = line.strip().split('\t')
            if (current_user_id) == user_id:
                updete_lines.append(f'{user_id}\t{new_grade}\t{name}\t{photo}\n')
            else: updete_lines.append(line)
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(updete_lines)


def get_user_from_db(my_user_id):
    with open(filename, 'r',encoding='utf-8') as file:
        #проверка содержимого файла
        for line in file:
            if len(line.strip().split("\t"))==4:
                user_id, grade, name, photo = line.strip().split('\t')
                if str(my_user_id) == user_id:
                    return {'user_id': user_id, 'class': grade, 'name': name, 'photo': photo}


def update_name_in_db(user_id, new_name):
    user_id = str(user_id)
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    update_lines = []
    for line in lines:
        if len(line.strip().split("\t")) == 4:
            current_user_id, grade, name, photo = line.strip().split('\t')
            if current_user_id == user_id:
                update_lines.append(f'{user_id}\t{grade}\t{new_name}\t{photo}\n')
            else:
                update_lines.append(line)
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(update_lines)


def update_photo_in_db(user_id, new_photo):
    user_id = str(user_id)
    with open(filename, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    update_lines = []
    for line in lines:
        if len(line.strip().split("\t")) == 4:
            current_user_id, grade, name, photo = line.strip().split('\t')
            if current_user_id == user_id:
                update_lines.append(f'{user_id}\t{grade}\t{name}\t{new_photo}\n')
            else:
                update_lines.append(line)
    with open(filename, 'w', encoding='utf-8') as file:
        file.writelines(update_lines)


if __name__ == '__main__':
    write_to_db('1234', '10н', 'Ира', 'нет фото')


#with open('text', 'r') as file:
    #for line in file:
       # print(line.strip().split('\t'))
    #file.write('\nAnother text')