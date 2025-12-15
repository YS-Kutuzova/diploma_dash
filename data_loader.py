import pandas as pd
import os

class SportDataLoader:
    
    def __init__(self, filename='sport_objects_final_full_data.csv'):
        self.filename = filename
        self.df = None  
        self.full_df = None 
        self.loaded = False
        
    def load(self):
        if self.loaded:
            return True
            
        try:            
            if not os.path.exists(self.filename):
                return False
            
            # Загружаем файл
            self.full_df = pd.read_csv(self.filename, encoding='utf-8')
            
            # Уникальные спортивные объекты
            if 'sport_object_id' in self.full_df.columns:
                # Группируем по ID объекта и берем первую строку для каждого - так как есть дублирование по object_id
                grouped = self.full_df.groupby('sport_object_id').first().reset_index()
                self.df = grouped
            else:
                self.df = self.full_df.drop_duplicates()
            
            self.loaded = True
            return True
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return False
    
    # df с уникальными объектами
    def get_objects(self):
        return self.df if self.df is not None else pd.DataFrame()
    
    # df со всеми записями
    def get_full_data(self):
        return self.full_df if self.full_df is not None else pd.DataFrame()
    
    # инфра для конкретного объекта
    def get_infrastructure_by_object(self, object_id):
        if self.full_df is None:
            return []
        
        # Фильтруем строки для данного объекта
        infra_rows = self.full_df[self.full_df['sport_object_id'] == object_id]
        
        # Возвращаем список с инфраструктурой
        result = []
        for _, row in infra_rows.iterrows():
            infra_item = {
                'type': str(row.get('infrastructure_type', 'Неизвестно')),
                'name': str(row.get('infrastructure_name', 'Без названия')),
                'address': str(row.get('infrastructure_address', 'Без адреса')),
                'distance': row.get('distance_meters', 0)
            }
            result.append(infra_item)
        
        return result
    
    # Получить список типов спорта с количеством объектов
    def get_sport_types_with_counts(self):
        if self.df is None or 'sport_object_type' not in self.df.columns:
            return []
        
        # Считаем количество объектов каждого типа
        type_counts = self.df['sport_object_type'].value_counts().reset_index()
        type_counts.columns = ['type', 'count']
        
        # Преобразуем в список
        result = []
        for _, row in type_counts.iterrows():
            result.append({
                'type': str(row['type']),
                'count': int(row['count'])
            })
        
        return result
    
    # Cписок уникальных районов
    def get_districts(self):
        if self.df is not None and 'district' in self.df.columns:
            districts = self.df['district'].dropna().unique().tolist()
            return sorted([str(d) for d in districts])
        return []
    
    # Cписок уникальных типов инфраструктуры
    def get_infrastructure_types(self):
        if self.full_df is not None and 'infrastructure_type' in self.full_df.columns:
            types = self.full_df['infrastructure_type'].dropna().unique().tolist()
            return sorted([str(t) for t in types])
        return []
    
    # Статитика
    def get_basic_statistics(self):
        if self.df is None or self.df.empty:
            return {}
        
        stats = {
            'total_objects': len(self.df),
            'unique_types': self.df['sport_object_type'].nunique() if 'sport_object_type' in self.df.columns else 0,
        }
        
        return stats
    
    # Cтатистикf по районам для анализа гипотез
    def get_district_statistics(self):
        if self.full_df is None or self.full_df.empty:
            return pd.DataFrame()
        
        # Список колонок для анализа
        district_cols = []
        
        # Проверяем наличие каждой колонки
        possible_cols = ['district', 'Плотность_населения', 'Зарплата', 
                        'Население', 'Соотношение_М_Ж', 'Кластер', 'Тип_кластера_района']
        
        for col in possible_cols:
            if col in self.full_df.columns:
                district_cols.append(col)
        
        if len(district_cols) < 1:  # Нужен хотя бы district
            return pd.DataFrame()
        
        # Берем только нужные колонки и удаляем дубликаты по районам
        district_stats = self.full_df[district_cols].drop_duplicates(subset=['district'])
        
        return district_stats
    
    def get_cluster_analysis_data(self):
        return self.get_district_statistics()

sport_data = SportDataLoader()