import pandas as pd
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm


# model config with main functions
class Model:
    def __init__(self, model_name):
        self.model = SentenceTransformer(model_name)
        self.standards_groups = pd.read_csv('standarts.csv')['Группа продукции'].unique()
        self.standards_groups_file = pd.read_csv('standarts.csv')

    def get_products_group_embeddings(self):
        # Получаем эмбеддинги для групп продуктов
        passage_embedding = self.model.encode(self.standards_groups)
        return passage_embedding

    def get_equipment_dictionary(self, most_similar):
        equipments = pd.read_csv('dataset_Equipment.csv')
        standards = self.standards_groups_file[self.standards_groups_file['Группа продукции']
                                               == most_similar]['Обозначение и наименование стандарта'].unique()
        equipment_dict = {}
        for standard in standards:
            for gost_name in equipments['gost'].unique():
                if standard.__contains__(gost_name):
                    eqt = equipments[equipments['gost'] == gost_name]['Equipment'].values
                    if eqt[0].__contains__('Оборудование не реглам'):
                        equipment_dict[gost_name] = ['Оборудование не регламентируется']
                    else:
                        equipment_dict[gost_name] = list(eqt)

        return equipment_dict

    def get_most_similar_value(self, product_name):
        # find similar product group by product name
        product_name_embedding = self.model.encode(product_name)  # получаем эмбеддинг наименования продукта
        similarities = util.dot_score(product_name_embedding, self.get_products_group_embeddings())[0]
        most_similar = pd.DataFrame({'similarity_score': similarities, 'standarts_groups': self.standards_groups}). \
                           sort_values(['similarity_score'], ascending=False)['standarts_groups'][:1].values[0]

        return most_similar

    def get_recommendation_card(self, query):
        most_similar_value = self.get_most_similar_value(product_name=query)
        equipment_dict = self.get_equipment_dictionary(most_similar=most_similar_value)
        message = f'Для \"{query}\" есть следующая информация по стандартам и ' \
                  f'оборудованию:\n'
        if len(equipment_dict.keys()) > 0:
            for idx, key in enumerate(equipment_dict.keys()):
                value = equipment_dict[key][0].replace("\n", " ")
                message += f'{idx + 1}. Для стандарта {key} необходимо следующее оборудование: {value}\n'
        return message

    def get_recommendation_card_simplified(self, equipment_dict, query):
        message = f'Для \"{query}\" есть следующая информация по стандартам и ' \
                  f'оборудованию:\n'
        if len(equipment_dict.keys()) > 0:
            for idx, key in enumerate(equipment_dict.keys()):
                value = equipment_dict[key][0].replace("\n", " ")
                message += f'{idx + 1}. Для стандарта {key} необходимо следующее оборудование: {value}\n'
        return message

    def preprocess_input_user_file(self, path):
        data = pd.read_csv(path, index_col=0)
        flag = []
        recommendation = []
        data['Обозначение стандарта'] = data['Обозначение стандарта'].apply(lambda x: x.split(', '))
        standards_lst = data['Обозначение стандарта'].values
        product_names = data['Наименование продукции'].values
        for standards, product_name in tqdm(zip(standards_lst, product_names)):
            most_similar = self.get_most_similar_value(product_name=product_name)
            equip_dict = self.get_equipment_dictionary(most_similar=most_similar)
            flag_value = 'n'
            for standard in standards:
                if standard in equip_dict.keys():
                    flag_value = 'y'
            flag.append(flag_value)
            recommendation.append(self.get_recommendation_card_simplified(equipment_dict=equip_dict, query=product_name))
        data['flag'] = flag
        data['recommendation'] = recommendation
        return data