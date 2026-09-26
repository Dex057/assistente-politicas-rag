# Reflexão

**Por que citar a FONTE.** A citação é o que permite conferir a resposta. Um assistente que
responde "até 3 dias por semana" sem dizer de onde tirou isso pede confiança cega: ninguém
consegue verificar, nem rastrear o erro quando a regra muda. Neste corpus o risco é concreto:
a POL-004 e a POL-005 dizem coisas diferentes sobre o mesmo assunto, e sem FONTE as duas
respostas parecem igualmente válidas. Em uma empresa real isso vira decisão errada tomada de
boa-fé, e ninguém sabe se a culpa foi do assistente, da política ou de quem leu.

**A decisão mais difícil.** Foi o threshold, mas só consegui tomá-la depois de resolver o
pré-processamento, pois as duas estão amarradas. Medi as oito combinações de acentos, stopwords e
inclusão da seção no índice: todas acertam 9 de 9, então Hit@1 não decidia nada. Troquei o
critério pela distância entre a pergunta respondível de pior score (P09, 0.368) e a pergunta
sem resposta (P10, 0.225). Remover stopwords triplica essa margem, de 0.042 para 0.143, porque
"quantos", "qual" e "posso" aparecem nas duas pontas e aproximam qualquer coisa de qualquer
coisa. Com a margem aberta, o 0.30 caiu quase no meio da lacuna, em vez de ser escolhido no
olho. O difícil não era o valor: era o critério que o sustentasse.

**Com um LLM.** A Parte 4 deixaria de copiar o chunk e passaria a redigir a partir dele,
resolvendo perguntas cuja resposta está espalhada em duas seções. O risco novo é a resposta
deixar de ser verificável: o modelo pode fundir a POL-004 revogada com a POL-005 vigente numa
frase fluente, com a FONTE certa no rodapé e o conteúdo errado no meio. Hoje o erro é da
política; com geração, passa a ser invisível.
