desc ='''
这个就是一个可以把字符串文本里面的地址解析出来并生成一个DataFrame的小包.
用法：
import yve_help
yve_help.transform(location_list)
注意一定是list啊

Dedicate this package to Yve
'''

myumap = {'南关区': '长春市',
          '南山区': '深圳市',
          '宝山区': '上海市',
          '市辖区': '东莞市',
          '普陀区': '上海市',
          '朝阳区': '北京市',
          '河东区': '天津市',
          '白云区': '广州市',
          '西湖区': '杭州市',
          '铁西区': '沈阳市',
          '龙华区': '深圳市'
          }


def transform(location_strs, umap=myumap):
    from mapper.transformer import ChloeTransformer
    cpca = YveTransformer(umap)
    return cpca.transform(location_strs)

#print(transform(['天津市南京路','北京市海淀区北三环西路满庭芳园','上海闸北区','深圳福田']))
