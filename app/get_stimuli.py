
import pandas as pd
import os

DEBUG=True
BASE_URL = 'http://10.30.12.152:5000'



def get_stim_ids(project='', filter=[]):
    
    stim_dir = 'data'
    
    stim_files = [f for f in os.listdir(stim_dir) if f.endswith('.csv')]

    id_dict = {}
 
    for sfile in stim_files:
        pname = sfile.replace('.csv','')
        if project in sfile:
            pdf = pd.read_csv(os.path.join(stim_dir, sfile))
            if filter:
                pdf=pdf[-pdf['id'].isin(filter)]
            
            if len(pdf['id'])>0:
                id_dict[pname]=pdf['id'].values

    return id_dict
    

def get_stim(project, stim_id):
    '''
    rough starting point for getting specific stim
    and doing project appropriate formatting to return
    the stim for server to pass to client
    '''
    
    
    # PA2 - stim id is of form "theme_type", e.g. "aging_how"
    # need to get text from stimuli CSV and matching image
    
    PA_html = '''
        <div id="stim">
            <figure>
                <img src="{ipath}"/>
                <figcaption>{mtext}</figcaption>
            </figure>
        
        </div>
    '''
    
    PA1_risk_html = '''
        <div id="stim">
            <h4>{mtext}</h4>
        </div>
    '''
    
    AS_html = '''
        <div id="stim">
            <figure>
                <img src="{ipath}"/>
            </figure>
        </div>
    '''
    
    P1_image_html = '''
        <div id="stim">
            <figure>
                <figcaption><h3>Stop Smoking. Start living.</h3></figcaption>
                <img src="{ipath}"/>
            </figure>
        </div>
    '''
    
    CY_html = '''
        <div id="stim">
            <figure>
                <figcaption><h4>{mtext}</h4></figcaption>
                <img width=400 src="{ipath}"/>
            </figure>
        </div>
    '''
    
    
    P1_banner_html = '''
        <div id="stim">
            <video controls>
              <source src="{vpath}" type="video/mp4">
            </video>
        </div>
    '''
    
    PSA_html = '''
        <div id="stim">
            <video  width="520" controls autoplay>
              <source src="{vpath}" type="video/mp4">
            </video>
        </div>
    '''
    
    rsm_MT_html = '''
        <div id="stim">
            <video  width="520" controls controlsList="nodownload" autoplay >
              <source src="{vpath}" type="video/mp4">
            </video>
        </div>
    '''
    
    
    DARPA_html = '''
        <div id="stim">
            <div>
                <h4>{headline}</h4>
                <p>{abstract}</p>
             </div>
        </div>
    '''
    
    
    WA_html = '''
        <div id="stim">
            <div>
            <h4>{statement}</h4>
            <audio controls controlsList="nodownload" 
                    src="{apath}">
            </audio>
            </div>
        </div>
    '''
    
    PROD_html = '''
        <div id="stim">
            <video  width="520" controls controlsList="nodownload nofullscreen" autoplay >
              <source src="{vpath}" type="video/mp4">
            </video>
        </div>
    '''
    
    SF_rate_html = '''
        <div id="stim">
            <figure>
                <img src="{ipath}"/>
            </figure>
        </div>
    '''

    SF_watch_html = '''
        <div id="stim">
            <video width="520" controls controlsList="nodownload no" autoplay >
              <source src="{vpath}" type="video/mp4">
            </video>
        </div>
    '''
    
    
    print('in gs', project, stim_id)
    
    if project=='PA1':
        
        image='null.png' if stim_id.startswith('risk_') else '{}.png'.format(stim_id)
        
        image_path = '{}/media/PA1/images/{}'.format(BASE_URL, image)

        
        pa1_df = pd.read_csv('../../stimuli/PA1/PA1_stimuli.csv')
        
        message_text = pa1_df[pa1_df['id']=='PA1-'+stim_id]['message'].values[0]
        
        if DEBUG:
            print(message_text)
        
        if image=='null.png':
            return PA1_risk_html.format(mtext=message_text)
        else:
            return PA_html.format(ipath=image_path, mtext=message_text)
    
    elif project=='PA2':
    
        theme, mtype = stim_id.split('_')
        
        if DEBUG:
            print(theme, mtype)
        
        pa2_df = pd.read_csv('../../stimuli/PA2/PA2_stimuli.csv')
        
        mrow = pa2_df[(pa2_df['theme']==theme) & (pa2_df['type']==mtype)]
        
        if DEBUG:
            print(mrow)
        
        if not mrow.shape[0]:
            return None
        
        message_text = mrow.iloc[0]['message']
        cond = mrow.iloc[0]['cond']
        
        if DEBUG:
            print(cond, message_text)
        image_path = '{}/media/PA2/images/{}/{}.png'.format(BASE_URL, cond, stim_id)
        
        #return {'ipath': image_path, 'mtext': message_text}
        
        return PA_html.format(ipath=image_path, mtext=message_text)
            
    elif project=='D1':
        aid = 'D1-{}'.format(stim_id)
        darpa1_df = pd.read_csv('../../stimuli/darpa1/darpa1_sharing_task_stimuli.csv')
        mrow = darpa1_df[darpa1_df['id']==aid]
        if DEBUG:
            print(mrow)
        
        headline = mrow.iloc[0]['headline']
        abstract = mrow.iloc[0]['abstract']
        
        return DARPA_html.format(headline=headline, abstract=abstract)
                
        
    elif project=='WA':
        aid = 'WA-{}'.format(stim_id)
        WA_df = pd.read_csv('../../stimuli/WA_walkstatement/walkstatement_stimuli.csv')
        mrow = WA_df[WA_df['id']==aid]
        if DEBUG:
            print(mrow)
        
        statement = mrow.iloc[0]['statement']
        afilename = mrow.iloc[0]['stim_file']
        
        audio_path = '{}/media/WA_walkstatement/audio/{}'.format(BASE_URL, afilename)

        
        return WA_html.format(statement=statement, 
                                 apath=audio_path)
                
                
        
    elif project=='P1':
        
            task = stim_id.split('_')[0]
        
            if DEBUG:
                print(stim_id)
                
            if task == 'image':
                set, sid = stim_id.split('_')[1:]
                image_path = '{}/media/project1/image_task/{}/{}.jpg'.format(BASE_URL,set,sid)

                return P1_image_html.format(ipath=image_path)
            elif task == 'banner':
                sid = stim_id.split('_')[1]
                
                vfile = [f for f in os.listdir('../../stimuli/project1/banner_task/new') if f.split('_')[1]==sid]
                print(vfile)
                vpath = '{}/media/project1/banner_task/new/{}'.format(BASE_URL, vfile[0])
                
                return P1_banner_html.format(vpath=vpath)
      
    elif project=='SF':
        
            task, sid = stim_id.split('_')
        
            if DEBUG:
                print("stim_id: {} task: {} sid: {}".format(stim_id, task, sid))
                
            if task == 'rate':
                image_path = '{}/media/SF/rate/{}.jpg'.format(BASE_URL,sid)

                return SF_rate_html.format(ipath=image_path)
            
            elif task == 'watch':
                vpath = '{}/media/SF/watch/{}.mp4'.format(BASE_URL, sid)
                
                return SF_watch_html.format(vpath=vpath)
    
    elif project=='CY':
        
        image_path = "{}/media/cityyear/cityyear.jpg".format(BASE_URL)
        
        cityyear_df = pd.read_csv('../../stimuli/cityyear/cityyear_stimuli.csv')
        mrow = cityyear_df[cityyear_df['code']==stim_id]
        if DEBUG:
            print(mrow)
        
        mtext = mrow.iloc[0]['message']        
        
        return CY_html.format(ipath=image_path, mtext=mtext)
            
    elif project=='AS':
        image_path = '{}/media/alcohol/{}.jpg'.format(BASE_URL, stim_id)                
        return AS_html.format(ipath=image_path)

    elif project=='PSA':
        
        df = pd.read_csv('data/PSA.csv')
        
        mtype, sid = stim_id.split('_')
        
        full_id = "PSA-{}".format(stim_id)

        if DEBUG:
            print('PSA', mtype, sid)
        
        vfile = df.loc[df['id']==full_id,'filename'].values[0]
        
        vfilename = "{}/{}".format(mtype, vfile)
                
        vpath = '{}/media/PSA/{}'.format(BASE_URL, vfilename)
                
        return PSA_html.format(vpath=vpath)
    
    elif project.startswith('rsm_'):
         
        sid = '{}-{}'.format(project,stim_id)
        
        df = pd.read_csv('data/{}.csv'.format(project))
    
        
        mrow = df[df['id']==sid]
        
        if DEBUG:
            print(mrow)   
        
        vfilename = mrow.iloc[0]['video_filename']
                
        project_folder = 'movietrailer' if project=='rsm_MT' else 'tvc35'
            
        vpath = '{}/media/rsm_{}/video/{}'.format(BASE_URL, project_folder, vfilename)
                
        return rsm_MT_html.format(vpath=vpath)
    
    elif project=='PROD':
        
        sid = 'PROD-{}'.format(stim_id)
        
        df = pd.read_csv('data/PROD.csv')
        
        mrow = df[df['id']==sid]
        
        if DEBUG:
            print(mrow)           
            
        vfilename = mrow.iloc[0]['fname']
                
        video_folder = mrow.iloc[0]['fpath']
            
        vpath = '{}/media/product/video/{}/{}'.format(BASE_URL, video_folder, vfilename)
        
        return PROD_html.format(vpath=vpath)