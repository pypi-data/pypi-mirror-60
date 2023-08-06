


# class Interpretation():
#     "Interpretation base class, can be inherited for task specific Interpretation classes"
#     def __init__(self, learn:Learner, preds:Tensor, y_true:Tensor, losses:Tensor, ds_type:DatasetType=DatasetType.Valid):
#         self.data,self.preds,self.y_true,self.losses,self.ds_type, self.learn = \
#                                  learn.data,preds,y_true,losses,ds_type,learn
#         self.ds = (self.data.train_ds if ds_type == DatasetType.Train else
#                    self.data.test_ds if ds_type == DatasetType.Test else
#                    self.data.valid_ds if ds_type == DatasetType.Valid else
#                    self.data.single_ds if ds_type == DatasetType.Single else
#                    self.data.fix_ds)

#     @classmethod
#     def from_learner(cls, learn: Learner,  ds_type:DatasetType=DatasetType.Valid, activ:nn.Module=None):
#         "Gets preds, y_true, losses to construct base class from a learner"
#         preds_res = learn.get_preds(ds_type=ds_type, activ=activ, with_loss=True)
#         return cls(learn, *preds_res)

#     def top_losses(self, k:int=None, largest=True):
#         "`k` largest(/smallest) losses and indexes, defaulting to all losses (sorted by `largest`)."
#         return self.losses.topk(ifnone(k, len(self.losses)), largest=largest)

#     # def top_scores(self, metric:Callable=None, k:int=None, largest=True):
#     #     "`k` largest(/smallest) metric scores and indexes, defaulting to all scores (sorted by `largest`)."
#     #     self.scores = metric(self.preds, self.y_true)
#     #     return self.scores.topk(ifnone(k, len(self.scores)), largest=largest)


# class ClassificationInterpretation(Interpretation):
#     "Interpretation methods for classification models."
#     def __init__(self, learn:Learner, preds:Tensor, y_true:Tensor, losses:Tensor, ds_type:DatasetType=DatasetType.Valid):
#         super().__init__(learn,preds,y_true,losses,ds_type)
#         self.pred_class = self.preds.argmax(dim=1)

#     def confusion_matrix(self, slice_size:int=1):
#         "Confusion matrix as an `np.ndarray`."
#         x=torch.arange(0,self.data.c)
#         if slice_size is None: cm = ((self.pred_class==x[:,None]) & (self.y_true==x[:,None,None])).sum(2)
#         else:
#             cm = torch.zeros(self.data.c, self.data.c, dtype=x.dtype)
#             for i in range(0, self.y_true.shape[0], slice_size):
#                 cm_slice = ((self.pred_class[i:i+slice_size]==x[:,None])
#                             & (self.y_true[i:i+slice_size]==x[:,None,None])).sum(2)
#                 torch.add(cm, cm_slice, out=cm)
#         return to_np(cm)

#     def plot_confusion_matrix(self, normalize:bool=False, title:str='Confusion matrix', cmap:Any="Blues", slice_size:int=1,
#                               norm_dec:int=2, plot_txt:bool=True, return_fig:bool=None, **kwargs)->Optional[plt.Figure]:
#         "Plot the confusion matrix, with `title` and using `cmap`."
#         # This function is mainly copied from the sklearn docs
#         cm = self.confusion_matrix(slice_size=slice_size)
#         if normalize: cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
#         fig = plt.figure(**kwargs)
#         plt.imshow(cm, interpolation='nearest', cmap=cmap)
#         plt.title(title)
#         tick_marks = np.arange(self.data.c)
#         plt.xticks(tick_marks, self.data.y.classes, rotation=90)
#         plt.yticks(tick_marks, self.data.y.classes, rotation=0)

#         if plot_txt:
#             thresh = cm.max() / 2.
#             for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
#                 coeff = f'{cm[i, j]:.{norm_dec}f}' if normalize else f'{cm[i, j]}'
#                 plt.text(j, i, coeff, horizontalalignment="center", verticalalignment="center", color="white" if cm[i, j] > thresh else "black")

#         ax = fig.gca()
#         ax.set_ylim(len(self.data.y.classes)-.5,-.5)
                           
#         plt.tight_layout()
#         plt.ylabel('Actual')
#         plt.xlabel('Predicted')
#         plt.grid(False)
#         if ifnone(return_fig, defaults.return_fig): return fig

#     def most_confused(self, min_val:int=1, slice_size:int=1)->Collection[Tuple[str,str,int]]:
#         "Sorted descending list of largest non-diagonal entries of confusion matrix, presented as actual, predicted, number of occurrences."
#         cm = self.confusion_matrix(slice_size=slice_size)
#         np.fill_diagonal(cm, 0)
#         res = [(self.data.classes[i],self.data.classes[j],cm[i,j])
#                 for i,j in zip(*np.where(cm>=min_val))]
#         return sorted(res, key=itemgetter(2), reverse=True)



