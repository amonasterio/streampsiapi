import streamlit as st, pandas as pd,json,time, urllib
from urllib.error import HTTPError
st.title("Consulta masiva a PSI")

api_key=st.text_input("API Key")
dispositivos = st.multiselect(
     'Seleccione dispositivos a analizar',
     ['mobile', 'desktop'],
     ['mobile', 'desktop'])
if api_key is not None and dispositivos is not None:
    f_entrada=st.file_uploader('CSV con URL a estudiar', type='csv')
    if f_entrada is not None:
        try:
            crawldf = pd.read_csv(f_entrada,header=None)
            addresses = crawldf[0].tolist()
            st.text(addresses)
            #dispositivos=['mobile','desktop']
            dct_arr=[]
            for row in addresses:
                analiza=row
                for dispo in dispositivos:
                    url = "https://www.googleapis.com/pagespeedonline/v5/runPagespeed?url="+analiza+"&key="+api_key+"&strategy="+dispo+"&locale=es"                  
                    try:
                        response = urllib.request.urlopen(url)
                        data = json.loads(response.read())  
                        psi_dict={}
                        psi_dict['url']=data["lighthouseResult"]["finalUrl"]
                        psi_dict['dispositivo']=dispo
                        psi_dict['score'] = data["lighthouseResult"]["categories"]["performance"]["score"]
                        psi_dict['fcp_chrux (ms)'] =data["loadingExperience"]["metrics"]["FIRST_CONTENTFUL_PAINT_MS"]["percentile"] #into seconds (/1000)
                        psi_dict['fcp_chrux_score'] = data["loadingExperience"]["metrics"]["FIRST_CONTENTFUL_PAINT_MS"]["category"]
                        if  data["loadingExperience"]["metrics"].get("FIRST_INPUT_DELAY_MS") != None:
                            psi_dict['fid_chrux (ms)'] = data["loadingExperience"]["metrics"]["FIRST_INPUT_DELAY_MS"]["percentile"] #into seconds (/1000)
                            psi_dict['fid_chrux_score'] = data["loadingExperience"]["metrics"]["FIRST_INPUT_DELAY_MS"]["category"]
                        else:
                            psi_dict['fid_chrux (ms)'] ="-"
                            psi_dict['fid_chrux_score'] = "-"
                        
                        if  data["loadingExperience"]["metrics"].get("LARGEST_CONTENTFUL_PAINT_MS") != None:
                            psi_dict['lcp_chrux (ms)'] = data["loadingExperience"]["metrics"]["LARGEST_CONTENTFUL_PAINT_MS"]["percentile"] #into seconds (/1000)
                            psi_dict['lcp_chrux_score'] = data["loadingExperience"]["metrics"]["LARGEST_CONTENTFUL_PAINT_MS"]["category"]
                        else:
                            psi_dict['lcp_chrux (ms)'] ="-"
                            psi_dict['lcp_chrux_score'] = "-"

                        if  data["loadingExperience"]["metrics"].get("CUMULATIVE_LAYOUT_SHIFT_SCORE") != None:
                            psi_dict['cls_chrux'] = data["loadingExperience"]["metrics"]["CUMULATIVE_LAYOUT_SHIFT_SCORE"]["percentile"]/100
                            psi_dict['cls_chrux_score'] = data["loadingExperience"]["metrics"]["CUMULATIVE_LAYOUT_SHIFT_SCORE"]["category"]
                        else:
                            psi_dict['cls_chrux'] ="-"
                            psi_dict['cls_chrux_score'] = "-"   
                        
                        psi_dict['fcp_lighthouse (ms)'] =data["lighthouseResult"]["audits"]["first-contentful-paint"]["numericValue"] #into seconds (/1000)
                        psi_dict['fcp_lighthouse_score'] =data["lighthouseResult"]["audits"]["first-contentful-paint"]["score"] 
                        psi_dict['lcp_lighthouse (ms)'] =data["lighthouseResult"]["audits"]["largest-contentful-paint"]["numericValue"] 
                        psi_dict['lcp_lighthouse_score'] =data["lighthouseResult"]["audits"]["largest-contentful-paint"]["score"] 
                        psi_dict['cls_lighthouse'] =round(data["lighthouseResult"]["audits"]["cumulative-layout-shift"]["numericValue"],3)
                        psi_dict['cls_lighthouse_score'] =data["lighthouseResult"]["audits"]["cumulative-layout-shift"]["score"] 
                        psi_dict['max_potential_fid (ms)'] =data["lighthouseResult"]["audits"]["max-potential-fid"]["numericValue"] 
                        psi_dict['max_potential_fid_score'] =data["lighthouseResult"]["audits"]["max-potential-fid"]["score"] 
                        
                        psi_dict['tbt (ms)']  = data["lighthouseResult"]["audits"]["total-blocking-time"]["numericValue"]
                        psi_dict['tbt_score'] = data["lighthouseResult"]["audits"]["total-blocking-time"]["score"]
                        

                        psi_dict['speed_index (ms)'] = round(data["lighthouseResult"]["audits"]["speed-index"]["numericValue"],1)
                        psi_dict['speed_index_score'] = data["lighthouseResult"]["audits"]["speed-index"]["score"]
                    
                        psi_dict['tti (ms)'] = round(data["lighthouseResult"]["audits"]["interactive"]["numericValue"],1)
                        psi_dict['tti_score']= data["lighthouseResult"]["audits"]["interactive"]["score"]

                        items=data["lighthouseResult"]["audits"]["resource-summary"]['details']["items"]

                        for elem in items:
                            if elem.get('resourceType')=='total':
                                psi_dict['total_size (KB)']=round(elem.get('transferSize')/1024,2)
                                psi_dict['total']=elem.get('requestCount')
                            elif elem.get('resourceType')=='stylesheet':
                                psi_dict['css_size (KB)']=round(elem.get('transferSize')/1024,2)
                                psi_dict['css']=elem.get('requestCount')
                            elif elem.get('resourceType')=='font':
                                psi_dict['fonts_size (KB)']=round(elem.get('transferSize')/1024,2)
                                psi_dict['fonts']=elem.get('requestCount')
                            elif elem.get('resourceType')=='image':
                                psi_dict['img_size (KB)']=round(elem.get('transferSize')/1024,2)
                                psi_dict['img']=elem.get('requestCount')
                            elif elem.get('resourceType')=='script':
                                psi_dict['js_size (KB)']=round(elem.get('transferSize')/1024,2)
                                psi_dict['js']=elem.get('requestCount')
                            elif elem.get('resourceType')=='document':
                                psi_dict['html_size (KB)']=round(elem.get('transferSize')/1024,2)
                                psi_dict['html']=elem.get('requestCount')
                            elif elem.get('resourceType')=='media':
                                psi_dict['media_size (KB)']=round(elem.get('transferSize')/1024,2)
                                psi_dict['media']=elem.get('requestCount')
                            elif elem.get('resourceType')=='other':
                                psi_dict['others_size (KB)']=round(elem.get('transferSize')/1024,2)
                                psi_dict['others']=elem.get('requestCount')
                            elif elem.get('resourceType')=='third-party':
                                psi_dict['third_party_size (KB)']=round(elem.get('transferSize')/1024,2)
                                psi_dict['third_party']=elem.get('requestCount')
                        dct_arr.append(psi_dict)
                    except HTTPError as e:
                        st.error('Error al procesar la petición: '+url)
                        psi_dict={}
                        psi_dict['url']=analiza
                        psi_dict['dispositivo']=dispo
                        dct_arr.append(psi_dict)
                    except KeyError as e:
                        st.error('Error al recuperar parámetro '+ e.args[0]+' en '+analiza)
                        psi_dict={}
                        psi_dict['url']=analiza
                        psi_dict['dispositivo']=dispo
                        dct_arr.append(psi_dict)
                    time.sleep(1) #delay para evitar que nos salga captcha
            df = pd.DataFrame(dct_arr)           
            st.download_button(
                label="Descargar como CSV",
                data=df.to_csv(index = False).encode('utf-8'),
                file_name='salida.csv',
                mime='text/csv',
            )
            st.dataframe(df)
        except FileNotFoundError as e:
            st.error("File not found: "+e.strerror)
        except pd.errors.EmptyDataError:
            st.error("No data")
        except pd.errors.ParserError:
            st.error("Parse error")
        except Exception as e:
            st.error("Some other exception")