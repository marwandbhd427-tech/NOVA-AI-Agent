def run_gui(callback):
    try:
        import tkinter as tk
        from tkinter import scrolledtext
    except Exception as e:print('GUI غير متوفر:',e);return False
    root=tk.Tk();root.title('NOVA AI V6.1');root.geometry('900x650')
    tk.Label(root,text='NOVA AI',font=('Arial',24,'bold')).pack(pady=10)
    chat=scrolledtext.ScrolledText(root,wrap=tk.WORD,font=('Arial',12));chat.pack(fill='both',expand=True,padx=12,pady=8)
    frame=tk.Frame(root);frame.pack(fill='x',padx=12,pady=10);entry=tk.Entry(frame,font=('Arial',13));entry.pack(side='left',fill='x',expand=True)
    def send(event=None):
        text=entry.get().strip()
        if not text:return
        entry.delete(0,'end');chat.insert('end','You: '+text+'\n')
        try:ans=callback(text)
        except Exception as e:ans='خطأ: '+str(e)
        chat.insert('end','NOVA: '+str(ans)+'\n\n');chat.see('end')
    tk.Button(frame,text='Send',command=send).pack(side='right',padx=8);entry.bind('<Return>',send);root.mainloop();return True
