using DataFrames
using JuMP,Cbc


function getProduct(ARR)
    p = 1
    for row in eachrow(ARR)
        idx = row[:digit] +1
        pi = 1
        if row[:value] == 1
            x = final_Prob[idx]
        else
            x = 1 - final_Prob[idx]
        end
        p = p * x
    end
end

println("start")

cats = readtable("JuliaData/cats.csv")
cats = unstack(cats,:digit,:id,:value)
cat_ids = names(cats)
cat_ids = map(String,cat_ids[2:size(cat_ids)[1]])

prices = readtable("JuliaData/prices.csv")
prob = readtable("JuliaData/prob.csv")
prob = unstack(prob,:digit,:parents,:prob)
prob_arr = convert(Array,prob[:,2:4])

#clean up
x = size(prob_arr)
for i = 1:x[1],j = 1:x[2]
    if ismissing(prob_arr[i,j])
        prob_arr[i,j] = 0
        #println(i,"  ",j)
    end
end

num_cats = size(cats)[2]
m = Model(solver=CbcSolver())

@variable(m, chooseParent[2:num_cats,[1,2]], Bin)
@constraint(m,chooseParent[:,1] + chooseParent[:,2] .<= 2)#can only use cat once
@constraint(m,sum(chooseParent[:,1]) == 1)
@constraint(m,sum(chooseParent[:,2]) == 1)
p1 = convert(Array, cats[1:256,2:num_cats]) * chooseParent[:,1]
p2 = convert(Array, cats[1:256,2:num_cats]) * chooseParent[:,2]

@variable(m, chooseProb[1:256,[0,1,2]], Bin)
rows = chooseProb[:,0] + chooseProb[:,1] + chooseProb[:,2]

@constraint(m,rows .== 1)
@constraint(m,p1 + p2 -1 .<= chooseProb[:,2])
@constraint(m,p1 + p2 -2*chooseProb[:,2] .<= chooseProb[:,1])
@constraint(m,1 - p1 - p2 .<= chooseProb[:,0])

final_Prob = (chooseProb[:,0] .* prob_arr[:,1]) + (chooseProb[:,1] .* prob_arr[:,2]) + (chooseProb[:,2] .* prob_arr[:,3])

#Now to construct optimization function made up of the tags
traits = readtable("JuliaData/traits.csv")
groups = groupby(traits,:tag)
g = groups[2]
geneticProb = map((x,y)-> if x == 0 1-y else y end ,g[:value],getindex(final_Prob,g[:digit]+1))
l = size(g)[1]
@variable(m,tagProduct[1:l])
for i in 1:l-1
    idx = l-i
    @constraint(m,tagProduct[idx] == geneticProb[i]*geneticProb[i+1])
end



@objective(m,Max,tagProduct[1])
solve(m)

#cat_x = dot(Array(1:size(cat_ids)[1]),getValue(chooseParent[:,1]))
#cat_y = dot(Array(1:size(cat_ids)[1]),getValue(chooseParent[:,2]))

#println(cat_ids[Integer(cat_x)],"    ",cat_ids[Integer(cat_y)])
#vals = getValue(p)


println("finished")
